import faker
import unittest
from scrubadub.filth import NationalInsuranceNumberFilth

from base import BaseTestCase


class GBNinoTestCase(unittest.TestCase, BaseTestCase):

    def test_nino_1(self):
        """
        BEFORE: My NI number is AZ 12 34 56 A
        AFTER:  My NI number is {{NATIONAL_INSURANCE_NUMBER}}
        """
        self.compare_before_after(locale='en_GB')

    def test_nino_2(self):
        """
        BEFORE: Enter a National Insurance number that is 2 letters, 6 numbers, then A, B, C or D, like AZ123456A.
        AFTER:  Enter a National Insurance number that is 2 letters, 6 numbers, then A, B, C or D, like {{NATIONAL_INSURANCE_NUMBER}}.
        """
        self.compare_before_after(locale='en_GB')

    def test_nino_3(self):
        """
        BEFORE: It’s on your National Insurance card, benefit letter, payslip or P60. For example, AZ 12 34 56 A.
        AFTER:  It’s on your National Insurance card, benefit letter, payslip or P60. For example, {{NATIONAL_INSURANCE_NUMBER}}.
        """
        self.compare_before_after(locale='en_GB')

    def test_nino_4(self):
        """
        BEFORE: Please verify the NI AZ 123456 A.
        AFTER:  Please verify the NI {{NATIONAL_INSURANCE_NUMBER}}.
        """
        self.compare_before_after(locale='en_GB')

    def test_nino_5(self):
        """
        BEFORE: The number is AZ 123 456 A.
        AFTER:  The number is {{NATIONAL_INSURANCE_NUMBER}}.
        """
        self.compare_before_after(locale='en_GB')

    def test_generate(self):
        class Faker:
            def ssn(self):
                return 'ZZ061251T'

        self.assertEqual(
            'ZZ061251T',
            NationalInsuranceNumberFilth.generate(faker=Faker()),
        )
