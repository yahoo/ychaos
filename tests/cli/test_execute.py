#  Copyright 2021, Yahoo
#  Licensed under the terms of the Apache 2.0 license. See the LICENSE file in the project root for terms
from argparse import Namespace
from pathlib import Path
from tempfile import NamedTemporaryFile
from unittest import TestCase

from ansible.executor.task_queue_manager import TaskQueueManager
from mockito import ANY, unstub, verify, when

from ychaos.cli.execute import Execute
from ychaos.cli.mock import MockApp
from ychaos.testplan.schema import TestPlan


class TestVerificationCommand(TestCase):

    cls = Execute

    def setUp(self) -> None:
        self.testplans_directory = (
            Path(__file__).joinpath("../../resources/testplans").resolve()
        )
        self.assertTrue(
            str(self.testplans_directory).endswith("tests/resources/testplans")
        )

    def test_execute_for_invalid_testplan_path(self):
        args = Namespace()
        args.cls = self.cls

        # Required Arguments for execute command
        args.testplan = self.testplans_directory.joinpath("valid/unknown.json")

        # Create a Mocked CLI App
        app = MockApp(args)
        args.app = app

        self.assertEqual(1, args.cls.main(args))

        self.assertTrue("valid/unknown.json not found" in app.get_console_output())

    def test_execute_for_machine_target_when_no_targets_found(self):
        temp_testplan_file = NamedTemporaryFile("w+")

        args = Namespace()
        args.cls = self.cls

        # Create a Mocked CLI App
        app = MockApp(args)
        args.app = app

        # Required Arguments for execute command
        testplan = TestPlan.load_file(
            self.testplans_directory.joinpath("valid/testplan2.yaml")
        )
        testplan.attack.target_config["blast_radius"] = 0
        testplan.export_to_file(temp_testplan_file.name)

        args.testplan = self.testplans_directory.joinpath(temp_testplan_file.name)

        self.assertEqual(0, args.cls.main(args))

        self.assertTrue(
            "No targets found for attack. Bailing out.." in app.get_console_output()
        )

    def test_execute_for_self_target(self):
        temp_testplan_file = NamedTemporaryFile("w+")

        args = Namespace()
        args.cls = self.cls

        app = MockApp(args)
        args.app = app

        testplan = TestPlan.load_file(
            self.testplans_directory.joinpath("valid/testplan6.yaml")
        )
        testplan.export_to_file(temp_testplan_file.name)

        args.testplan = self.testplans_directory.joinpath(temp_testplan_file.name)

        when(TaskQueueManager).run(ANY).thenReturn(True)

        self.assertEqual(0, args.cls.main(args))
        self.assertTrue("Starting attack. executor=self" in app.get_console_output())
        verify(TaskQueueManager, times=1).run(ANY)

    def tearDown(self) -> None:
        unstub()
