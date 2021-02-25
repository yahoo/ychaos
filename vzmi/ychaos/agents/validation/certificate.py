#  Copyright 2021, Verizon Media
#  Licensed under the terms of the ${MY_OSI} license. See the LICENSE file in the project root for terms

from datetime import datetime, timedelta, timezone
from socket import gaierror, timeout
from typing import List

from pydantic import AnyHttpUrl, Field, validate_arguments

from vzmi.ychaos.agents.agent import (
    Agent,
    AgentConfig,
    AgentMonitoringDataPoint,
    AgentPriority,
)
from vzmi.ychaos.utils.dependency import DependencyUtils

(X509,) = DependencyUtils.import_from(
    "OpenSSL.crypto",
    ("X509",),
)

pyopenssl = DependencyUtils.import_module("requests.packages.urllib3.contrib.pyopenssl")


class ServerCertValidationConfig(AgentConfig):
    name = "server_cert_validation"
    desc = "This minion retrieves SSL certificates from server and validates it"
    priority = AgentPriority.LOW_PRIORITY

    urls: List[AnyHttpUrl] = Field(
        default=list(),
        description="List of URLs which will be validated for their SSL certificate expiry",
        min_items=1,
    )
    expiry_threshold: timedelta = Field(
        default=timedelta(days=7), description="Expiry threshold"
    )

    timeout: int = Field(
        default=5, description="Default timeout to fetch the certificates in seconds"
    )


class ServerCertValidation(Agent):
    @validate_arguments
    def __init__(self, config: ServerCertValidationConfig):
        super(ServerCertValidation, self).__init__(config)

    def monitor(self):
        return self._status

    def setup(self) -> None:
        super(ServerCertValidation, self).setup()

    @staticmethod
    def get_server_cert(host: str, port: int, timeout_=5):
        from socket import setdefaulttimeout

        setdefaulttimeout(timeout_)

        assert pyopenssl is not None
        return pyopenssl.OpenSSL.crypto.load_certificate(
            pyopenssl.OpenSSL.crypto.FILETYPE_PEM,
            pyopenssl.ssl.get_server_certificate((host, port)),
        )

    def run(self) -> None:
        for url in self.config.urls:
            if url.port is None:
                url.port = "443"

            data = dict(host=url.host, port=int(url.port), error=None)

            try:
                cert = self.get_server_cert(
                    url.host, int(url.port), timeout_=self.config.timeout
                )
                cert_expiry_date = datetime.strptime(
                    cert.get_notAfter().decode("ascii"), "%Y%m%d%H%M%SZ"
                )
                cert_expiry_date.replace(tzinfo=timezone.utc)

                data.update(
                    dict(
                        not_valid_after=cert_expiry_date,
                        is_expired=datetime.utcnow() >= cert_expiry_date,
                        is_critical=datetime.utcnow() + self.config.expiry_threshold
                        >= cert_expiry_date,
                    )
                )
            except (timeout, gaierror) as error:
                data.update(error=str(error.__class__.__name__))

            self._status.put(
                AgentMonitoringDataPoint(
                    data=data,
                    state=self.current_state,
                )
            )

    def teardown(self) -> None:
        super(ServerCertValidation, self).teardown()
