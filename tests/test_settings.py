#  Copyright 2021, Yahoo
#  Licensed under the terms of the Apache 2.0 license. See the LICENSE file in the project root for terms
from unittest import TestCase

from ychaos.settings import ApplicationSettings, ProdSettings, Settings


class TestSettings(TestCase):
    def test_settings_with_no_config_creates_ProdSettings_configuration(self):
        result_settings = Settings.get_instance()
        self.assertIsInstance(result_settings, ProdSettings)

    def test_settings_with_unknown_configuration(self):
        with self.assertRaises(Exception):
            Settings("unknown_config")

    def test_settings_get_version(self):
        app_settings = ApplicationSettings.get_instance()
        self.assertIsNotNone(app_settings.get_version())
