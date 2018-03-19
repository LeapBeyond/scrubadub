import unittest

from base import BaseTestCase


class PhoneNumberTestCase(unittest.TestCase, BaseTestCase):

    def create_clean_docstring(self, phone_number):
        return """
        BEFORE: My phone number is %s
        AFTER:  My phone number is {{PHONE}}
        """ % phone_number

    def create_scan_docstring(self, phone_number):
        return """
        BEFORE: My phone number is %s
        AFTER:  phone
        """ % phone_number

    def check_clean_phone_numbers(self, *phone_numbers):
        for phone_number in phone_numbers:
            self.compare_clean_before_after(
                docstring=self.create_clean_docstring(phone_number),
            )

    def check_scan_of_phone_numbers(self, *phone_numbers):
        for phone_number in phone_numbers:
            self.compare_scan_before_after(
                docstring=self.create_scan_docstring(phone_number),
            )

    def test_clean_american_phone_number(self):
        """test american-style phone numbers"""
        self.check_clean_phone_numbers(
            '1-312-515-2239',
            '+1-312-515-2239',
            '1 (312) 515-2239',
            '312-515-2239',
            '(312) 515-2239',
            '(312)515-2239',
        )

    def test_scan_american_phone_number(self):
        """test american-style phone numbers"""
        self.check_scan_of_phone_numbers(
            '1-312-515-2239',
            '+1-312-515-2239',
            '1 (312) 515-2239',
            '312-515-2239',
            '(312) 515-2239',
            '(312)515-2239',
        )

    def test_clean_extension_phone_numbers(self):
        """test phone numbers with extensions"""
        self.check_clean_phone_numbers(
            '312-515-2239 x12',
            '312-515-2239 ext. 12',
            '312-515-2239 ext.12',
        )

    def test_clean_international_phone_numbers(self):
        """test international phone numbers"""
        self.check_clean_phone_numbers(
            '+47 21 30 85 99',
            '+45 69 19 88 56',
            '+46 852 503 499',
            '+31 619 837 236',
            '+86 135 3727 4136',
            '+61267881324',
        )

    def test_clean_multiple_phone_numbers(self):
        # running this through scrubadub.clean replaces 'reached at
        # 312.714.8142' with '{{EMAIL}}'. See issue
        result = self.clean(
            u'Call me on my cell 312.714.8142 or in my office 773.415.7432'
        )
        self.assertEqual(
            result,
            u'Call me on my cell {{PHONE}} or in my office {{PHONE}}',
            'problem with multiple phone numbers: \n %s' % result,
        )

    def test_scan_multiple_phone_numbers(self):
        # running this through scrubadub.clean replaces 'reached at
        # 312.714.8142' with '{{EMAIL}}'. See issue
        result = self.scan(
            u'Call me on my cell 312.714.8142 or in my office 773.415.7432'
        )

        result = ''.join(result)

        self.assertEqual(
            result,
            u'phone',
            'problem with multiple phone numbers: \n %s' % result,
        )
