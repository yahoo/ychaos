#!/usr/bin/env python
"""
test_ychaos
----------------------------------

Tests for the 'vzmi.ychaos' module.
"""
import unittest


class TestImport(unittest.TestCase):
    def test__module__import(self):
        import vzmi.ychaos


if __name__ == "__main__":
    unittest.main()
