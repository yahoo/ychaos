#  Copyright 2021, Yahoo
#  Licensed under the terms of the Apache 2.0 license. See the LICENSE file in the project root for terms

from datetime import datetime, timedelta, timezone
from pathlib import Path
from queue import LifoQueue
from socket import gaierror, timeout
from types import SimpleNamespace
from typing import List, Union

from pydantic import (
    AnyHttpUrl,
    BaseModel,
    Field,
    FilePath,
    validate_arguments,
    validator,
)

from ...utils.builtins import AEnum
from ...utils.dependency import DependencyUtils
from ..agent import Agent, AgentConfig, AgentMonitoringDataPoint, AgentPriority
from ..utils.annotations import log_agent_lifecycle

(X509,) = DependencyUtils.import_from(
    "OpenSSL.crypto",
    ("X509",),
)

pyopenssl = DependencyUtils.import_module("requests.packages.urllib3.contrib.pyopenssl")


class ServerCertValidationConfig(AgentConfig):
    name = "server_cert_validation"
    desc = "This agent retrieves SSL certificates from server and validates it"
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

    def monitor(self) -> LifoQueue:
        super(ServerCertValidation, self).monitor()
        return self._status

    @log_agent_lifecycle
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

    @log_agent_lifecycle
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

    @log_agent_lifecycle
    def teardown(self) -> None:
        super(ServerCertValidation, self).teardown()


class CertificateFileType(AEnum):
    """
    Attributes:
        ASN1: (asn1) ASN1 Certificate format
        PEM: (pem) PEM Certificate format
    """

    ASN1 = "asn1", SimpleNamespace(binder=pyopenssl.OpenSSL.crypto.FILETYPE_ASN1)  # type: ignore
    PEM = "pem", SimpleNamespace(binder=pyopenssl.OpenSSL.crypto.FILETYPE_PEM)  # type: ignore


class CertificateFileConfig(BaseModel):
    path: FilePath = Field(..., description="Path to the certificate file")
    type: CertificateFileType = Field(
        default=CertificateFileType.PEM, description="Type of the certificate file"
    )


class CertificateFileValidationConfig(AgentConfig):
    name = "cert_file_validation"
    desc = "This agent decodes the local certificates and validates for expiry/critical"
    priority = AgentPriority.LOW_PRIORITY

    expiry_threshold: timedelta = Field(
        default=timedelta(days=7), description="Expiry threshold"
    )

    paths: List[Union[FilePath, CertificateFileConfig]] = Field(
        default=list(),
        description="List of Certificate files to be validated",
        min_items=1,
    )

    @validator("paths", each_item=True)
    def parse_paths(cls, v, values):
        if isinstance(v, Path):
            return CertificateFileConfig(path=v)
        return v


class CertificateFileValidation(Agent):
    def monitor(self) -> LifoQueue:
        super(CertificateFileValidation, self).monitor()
        return self._status

    @log_agent_lifecycle
    def setup(self) -> None:
        super(CertificateFileValidation, self).setup()

    @log_agent_lifecycle
    def run(self) -> None:
        super(CertificateFileValidation, self).run()
        for cert_path_config in self.config.paths:
            data = dict(
                path=str(cert_path_config.path),
                type=cert_path_config.type.value,
                error=None,
            )
            try:
                assert pyopenssl is not None
                cert = pyopenssl.OpenSSL.crypto.load_certificate(
                    cert_path_config.type.metadata.binder,
                    cert_path_config.path.read_bytes(),
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
            except pyopenssl.OpenSSL.crypto.Error:  # type: ignore
                data.update(error="decoding_error")

            self._status.put(
                AgentMonitoringDataPoint(
                    data=data,
                    state=self.current_state,
                )
            )

    @log_agent_lifecycle
    def teardown(self) -> None:
        super(CertificateFileValidation, self).teardown()
