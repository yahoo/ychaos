#  Copyright 2021, Verizon Media
#  Licensed under the terms of the ${MY_OSI} license. See the LICENSE file in the project root for terms

import logging
from io import StringIO
from unittest import TestCase

from ychaos.utils.logging import StructLogger


class TestStructLogger(TestCase):
    def setUp(self) -> None:
        self.stream = StringIO()
        self.handler = logging.StreamHandler(self.stream)
        self.logger = StructLogger("test")
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(self.handler)

    def test_struct_log_info(self):
        self.logger.info(
            "testMessage", testKwarg1="testValue1", testKwarg2="testValue2"
        )
        self.assertEqual(
            self.stream.getvalue().strip(),
            "testKwarg1=testValue1 testKwarg2=testValue2 testMessage",
        )

    def test_struct_log_info_when_not_enabled(self):
        self.logger.setLevel(logging.INFO + 1)
        self.logger.info(
            "testMessage", testKwarg1="testValue1", testKwarg2="testValue2"
        )
        self.assertEqual(
            self.stream.getvalue(),
            "",
        )

    def test_struct_log_debug(self):
        self.logger.debug(
            "testMessage", testKwarg1="testValue1", testKwarg2="testValue2"
        )
        self.assertEqual(
            self.stream.getvalue().strip(),
            "testKwarg1=testValue1 testKwarg2=testValue2 testMessage",
        )

    def test_struct_log_debug_when_not_enabled(self):
        self.logger.setLevel(logging.DEBUG + 1)
        self.logger.debug(
            "testMessage", testKwarg1="testValue1", testKwarg2="testValue2"
        )
        self.assertEqual(
            self.stream.getvalue(),
            "",
        )

    def test_struct_log_warning(self):
        self.logger.warning(
            "testMessage", testKwarg1="testValue1", testKwarg2="testValue2"
        )
        self.assertEqual(
            self.stream.getvalue().strip(),
            "testKwarg1=testValue1 testKwarg2=testValue2 testMessage",
        )

    def test_struct_log_warning_when_not_enabled(self):
        self.logger.setLevel(logging.WARNING + 1)
        self.logger.warning(
            "testMessage", testKwarg1="testValue1", testKwarg2="testValue2"
        )
        self.assertEqual(
            self.stream.getvalue(),
            "",
        )

    def test_struct_log_error(self):
        self.logger.error(
            "testMessage", testKwarg1="testValue1", testKwarg2="testValue2"
        )
        self.assertEqual(
            self.stream.getvalue().strip(),
            "testKwarg1=testValue1 testKwarg2=testValue2 testMessage",
        )

    def test_struct_log_error_when_not_enabled(self):
        self.logger.setLevel(logging.ERROR + 1)
        self.logger.error(
            "testMessage", testKwarg1="testValue1", testKwarg2="testValue2"
        )
        self.assertEqual(
            self.stream.getvalue(),
            "",
        )

    def test_struct_log_exception(self):
        self.logger.exception(
            "testMessage",
            testKwarg1="testValue1",
            testKwarg2="testValue2",
            exc_info=Exception(),
        )
        self.assertEqual(
            self.stream.getvalue().strip(),
            "testKwarg1=testValue1 testKwarg2=testValue2 testMessage\nException",
        )

    def test_struct_log_exception_when_not_enabled(self):
        self.logger.setLevel(logging.ERROR + 1)
        self.logger.exception(
            "testMessage", testKwarg1="testValue1", testKwarg2="testValue2"
        )
        self.assertEqual(
            self.stream.getvalue(),
            "",
        )

    def test_struct_log_invalid_level_when_raiseException_set_to_false(self):
        logging.raiseExceptions = False
        self.logger.log(
            "invalidLevel",
            "testMessage",
            testKwarg1="testValue1",
            testKwarg2="testValue2",
        )
        self.assertEqual(self.stream.getvalue().strip(), "")

    def test_get_child(self):
        self.logger.bind(testKwarg="testValue")
        child_logger = self.logger.getChild("testChild")
        self.assertEqual(child_logger.name, "test.testChild")
        self.assertDictEqual(child_logger._binder, dict())

        self.logger.unbind()
        self.assertDictEqual(self.logger._binder, dict())

    def test_unbind(self):
        self.logger.bind(testKwarg1="testValue1", testKwarg2="testValue2")
        self.assertDictEqual(
            self.logger._binder, dict(testKwarg1="testValue1", testKwarg2="testValue2")
        )

        self.logger.unbind({"testKwarg1"})
        self.assertDictEqual(self.logger._binder, dict(testKwarg2="testValue2"))

        self.logger.bind(testKwarg1="testValue1", testKwarg2="testValue2")
        self.logger.unbind()
        self.assertDictEqual(self.logger._binder, dict())

    def test_get_child_with_parent_bindings(self):
        self.logger.bind(testKwarg="testValue")
        child_logger = self.logger.getChild("testChild", bind_parent_attributes=True)
        self.assertEqual(child_logger.name, "test.testChild")
        self.assertDictEqual(child_logger._binder, dict(testKwarg="testValue"))

    def tearDown(self) -> None:
        self.stream.close()
