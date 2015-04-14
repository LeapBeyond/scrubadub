import unittest

import scrubadub

from base import BaseTestCase


class NameTestCase(unittest.TestCase, BaseTestCase):

    def test_john(self):
        """
        BEFORE: John is a cat
        AFTER:  {{NAME}} is a cat
        """
        self.compare_before_after()
