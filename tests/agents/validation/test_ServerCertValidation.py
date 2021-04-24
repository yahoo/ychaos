#  Copyright 2021, Verizon Media
#  Licensed under the terms of the ${MY_OSI} license. See the LICENSE file in the project root for terms
from unittest import TestCase

from vzmi.ychaos.agents.agent import AgentMonitoringDataPoint
from vzmi.ychaos.agents.validation.certificate import (
    ServerCertValidation,
    ServerCertValidationConfig,
)


class TestServerCertValidation(TestCase):
    def test_server_cert_validation_never_fails_for_yahoo(self):
        config = ServerCertValidationConfig(
            urls=[
                "https://www.yahoo.com",
                "https://unknownendpoint.com:4443",
                "https://yahoo.com",
            ]
        )

        agent = ServerCertValidation(config)
        agent.setup()
        agent.run()

        datapoint2: AgentMonitoringDataPoint = agent._status.get()
        data = datapoint2.data

        self.assertEqual(data["host"], "yahoo.com")
        self.assertIsNone(data["error"])
        self.assertEqual(data["port"], 443)
        self.assertFalse(data["is_expired"])
        self.assertFalse(data["is_critical"])

        datapoint1: AgentMonitoringDataPoint = agent._status.get()
        data = datapoint1.data

        self.assertEqual(data["host"], "unknownendpoint.com")
        self.assertIsNotNone(data["error"])
        self.assertEqual(data["port"], 4443)

        # Coverage
        agent.teardown()
        agent.monitor()
