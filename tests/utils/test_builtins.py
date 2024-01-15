#  Copyright 2021, Yahoo
#  Licensed under the terms of the Apache 2.0 license. See the LICENSE file in the project root for terms
from types import SimpleNamespace
from unittest import TestCase

from ychaos.utils.builtins import FQDN, AEnum, BuiltinUtils


class TestFQDN(TestCase):
    def test_fqdn_length_exceeded_max_limits(self):
        with self.assertRaises(ValueError):
            FQDN(f"yaho{'o' * 255}o.com")

    def test_fqdn_init_for_invalid_fqdn(self):
        with self.assertRaises(ValueError):
            FQDN(f"yahoo..com")

    def test_fqdn_for_valid_fqdn(self):
        self.assertEqual("yahoo.com", FQDN("yahoo.com"))


class TestFloat(TestCase):
    def test_float_non_parsable_value(self):
        self.assertEqual(0, BuiltinUtils.Float.parse("unknownFloat", 0))


class TestAEnum(TestCase):
    class MockTestEnum(AEnum):
        A = "a", SimpleNamespace(__aliases__=("1", 1))
        B = "b", SimpleNamespace(__aliases__=("2", 2))

    def test_resolve_alias(self):
        # Valid Alias
        self.assertEqual(self.MockTestEnum.A, self.MockTestEnum("1"))

        # Missing Alias
        with self.assertRaises(ValueError):
            self.MockTestEnum("3")


class TestOscSequenceSanitizer(TestCase):
    def test_validate(self):
        self.assertEqual('https://exam\n\n\ntesttesttest\n\n\n/', BuiltinUtils.OscSequenceSanitizer.validate(
            "https://exam\n\n\n\x1b[1;35mtest\x1b[1;34mtest\x1b[1;33mtest\n\n\n\e]52;c;/"))
