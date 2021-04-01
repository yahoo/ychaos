#  Copyright 2021, Verizon Media
#  Licensed under the terms of the ${MY_OSI} license. See the LICENSE file in the project root for terms
from unittest import TestCase

from vzmi.ychaos.utils.hooks import EventHook, InvalidEventHookError


class MockEventHook(EventHook):
    __hook_events__ = ("on_valid_hooks",)

    def mocked_method_that_calls_valid_hooks(self):
        self.execute_hooks("on_valid_hooks")

    def mocked_method_that_calls_invalid_hooks(self):
        self.execute_hooks("unknown_event")


class TestEventHook(TestCase):
    def test_register_hook_for_unknown_event(self):
        event_hook_object = MockEventHook()
        with self.assertRaises(InvalidEventHookError):
            event_hook_object.register_hook(
                "unknown_event", lambda: self.assertTrue(True)
            )

    def test_execute_hook_for_unknown_event(self):
        event_hook_object = MockEventHook()
        with self.assertRaises(InvalidEventHookError):
            event_hook_object.mocked_method_that_calls_invalid_hooks()

    class MockInactiveHook:
        active = False

        def __call__(self, *args, **kwargs):
            # Should never enter this method.
            # If enters, it will always fail
            assert 1 == 0

    def test_hooks_not_called_if_inactive(self):
        event_hook_object = MockEventHook()
        event_hook_object.register_hook("on_valid_hooks", self.MockInactiveHook())
        event_hook_object.mocked_method_that_calls_valid_hooks()
