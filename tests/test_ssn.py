import unittest

from base import BaseTestCase


class SSNTestCase(unittest.TestCase, BaseTestCase):

    def test_clean_hyphens(self):
        """
        BEFORE: My social security number is 812-80-1276
        AFTER:  My social security number is {{SSN}}
        """
        self.compare_clean_before_after()

    def test_clean_dots(self):
        """
        BEFORE: My social security number is 812.80.1276
        AFTER:  My social security number is {{SSN}}
        """
        self.compare_clean_before_after()

    def test_clean_spaces(self):
        """
        BEFORE: My social security number is 812 80 1276
        AFTER:  My social security number is {{SSN}}
        """
        self.compare_clean_before_after()

    def test_scan_hyphens(self):
        """
        BEFORE: My social security number is 812-80-1276
        AFTER:  ssn
        """
        self.compare_scan_before_after()

    def test_scan_dots(self):
        """
        BEFORE: My social security number is 812.80.1276
        AFTER:  ssn
        """
        self.compare_scan_before_after()

    def test_scan_spaces(self):
        """
        BEFORE: My social security number is 812 80 1276
        AFTER:  ssn
        """
        self.compare_scan_before_after()
