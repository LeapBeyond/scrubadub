import unittest

from base import BaseTestCase


class GBTrnTestCase(unittest.TestCase, BaseTestCase):

    def test_gbtrn_1(self):
        """
        BEFORE: My PAYE temp number is 99L99999, which is not permanent.
        AFTER:  My PAYE temp number is {{TAX_REFERENCE_NUMBER}}, which is not permanent.
        """
        self.compare_before_after(locale='en_GB')

    def test_gbtrn_2(self):
        """
        BEFORE: Enter a Temporary Reference Number that is 2 numbers, 1 letter, then 5 numbers, like 11 A 12345.
        AFTER:  Enter a Temporary Reference Number that is 2 numbers, 1 letter, then 5 numbers, like {{TAX_REFERENCE_NUMBER}}.
        """
        self.compare_before_after(locale='en_GB')

    def test_gbtrn_3(self):
        """
        BEFORE: It’s on your National Insurance card, benefit letter, payslip or P60. For example, 99L 99999.
        AFTER:  It’s on your National Insurance card, benefit letter, payslip or P60. For example, {{TAX_REFERENCE_NUMBER}}.
        """
        self.compare_before_after(locale='en_GB')

    def test_gbtrn_4(self):
        """
        BEFORE: Please verify the TRN 99 L 999 99.
        AFTER:  Please verify the TRN {{TAX_REFERENCE_NUMBER}}.
        """
        self.compare_before_after(locale='en_GB')

    def test_gbtrn_5(self):
        """
        BEFORE: The number is 11A 12345.
        AFTER:  The number is {{TAX_REFERENCE_NUMBER}}.
        """
        self.compare_before_after(locale='en_GB')
