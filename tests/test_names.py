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

    def test_no_names(self):
        """
        BEFORE: Hello. Please testing.
        AFTER: Hello. Please testing.
        """
        self.compare_before_after()

    @unittest.skip('lower names cause problems for textblob')
    def test_lower_names(self):
        """
        BEFORE: sarah is a friendly person
        AFTER: {{NAME}} is a friendly person
        """
        self.compare_before_after()
