import unittest

from base import BaseTestCase


class UKNinoTestCase(unittest.TestCase, BaseTestCase):

    def test_nino_1(self):
        """
        BEFORE: My NI number is QQ 12 34 56 C
        AFTER:  My NI number is {{UKNINO}}
        """
        self.compare_before_after()

    def test_nino_2(self):
        """
        BEFORE: Enter a National Insurance number that is 2 letters, 6 numbers, then A, B, C or D, like QQ123456C.
        AFTER:  Enter a National Insurance number that is 2 letters, 6 numbers, then A, B, C or D, like {{UKNINO}}.
        """
        self.compare_before_after()

    def test_nino_3(self):
        """
        BEFORE: It’s on your National Insurance card, benefit letter, payslip or P60. For example, QQ 12 34 56 C.
        AFTER:  It’s on your National Insurance card, benefit letter, payslip or P60. For example, {{UKNINO}}.
        """
        self.compare_before_after()

    def test_nino_4(self):
        """
        BEFORE: Please verify the NI QQ 123456 C.
        AFTER:  Please verify the NI {{UKNINO}}.
        """
        self.compare_before_after()

    def test_nino_5(self):
        """
        BEFORE: The number is QQ 123 456 C.
        AFTER:  The number is {{UKNINO}}.
        """
        self.compare_before_after()