#  Copyright 2021, Verizon Media
#  Licensed under the terms of the ${MY_OSI} license. See the LICENSE file in the project root for terms
from unittest import TestCase

from vzmi.ychaos.utils.builtins import FQDN


class TestFQDN(TestCase):
    def test_fqdn_length_exceeded_max_limits(self):
        with self.assertRaises(ValueError):
            FQDN(f"yaho{'o'* 255}o.com")

    def test_fqdn_init_for_invalid_fqdn(self):
        with self.assertRaises(ValueError):
            FQDN(f"yahoo..com")

    def test_fqdn_for_valid_fqdn(self):
        self.assertEqual("yahoo.com", FQDN("yahoo.com"))
