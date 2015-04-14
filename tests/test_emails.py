import unittest

from base import BaseTestCase


class EmailTestCase(unittest.TestCase, BaseTestCase):

    def test_gmail_john(self):
        """
        BEFORE: My email is john@gmail.com
        AFTER:  My email is {{EMAIL}}
        """
        self.compare_before_after()

    def test_fancy_gmail_john(self):
        """
        BEFORE: My email is john at gmail.com
        AFTER:  My email is {{EMAIL}}
        """
        self.compare_before_after()
