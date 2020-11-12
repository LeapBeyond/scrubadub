import unittest

from base import BaseTestCase


class GBNinoTestCase(unittest.TestCase, BaseTestCase):

    def test_nino_1(self):
        """
        BEFORE: My NI number is AZ 12 34 56 A
        AFTER:  My NI number is {{GBNINO}}
        """
        self.compare_before_after()

    def test_nino_2(self):
        """
        BEFORE: Enter a National Insurance number that is 2 letters, 6 numbers, then A, B, C or D, like AZ123456A.
        AFTER:  Enter a National Insurance number that is 2 letters, 6 numbers, then A, B, C or D, like {{GBNINO}}.
        """
        self.compare_before_after()

    def test_nino_3(self):
        """
        BEFORE: It’s on your National Insurance card, benefit letter, payslip or P60. For example, AZ 12 34 56 A.
        AFTER:  It’s on your National Insurance card, benefit letter, payslip or P60. For example, {{GBNINO}}.
        """
        self.compare_before_after()

    def test_nino_4(self):
        """
        BEFORE: Please verify the NI AZ 123456 A.
        AFTER:  Please verify the NI {{GBNINO}}.
        """
        self.compare_before_after()

    def test_nino_5(self):
        """
        BEFORE: The number is AZ 123 456 A.
        AFTER:  The number is {{GBNINO}}.
        """
        self.compare_before_after()
