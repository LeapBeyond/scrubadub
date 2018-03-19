import unittest

from base import BaseTestCase


class EmailTestCase(unittest.TestCase, BaseTestCase):

    def test_clean_gmail_john(self):
        """
        BEFORE: My email is john@gmail.com
        AFTER:  My email is {{EMAIL}}
        """
        self.compare_clean_before_after()

    def test_clean_fancy_gmail_john(self):
        """
        BEFORE: My email is john at gmail.com
        AFTER:  My email is {{EMAIL}}
        """
        self.compare_clean_before_after()

    def test_scan_gmail_john(self):
        """
        BEFORE: My email is john@gmail.com
        AFTER:  email
        """
        self.compare_scan_before_after()

    def test_scan_fancy_gmail_john(self):
        """
        BEFORE: My email is john at gmail.com
        AFTER:  email
        """
        self.compare_scan_before_after()
