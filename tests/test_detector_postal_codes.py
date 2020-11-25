import unittest
import warnings

import scrubadub

class PostalCodesTestCase(unittest.TestCase):

    def test_bad_locale(self):
        """test a non existant region"""
        with self.assertRaises(ValueError):
            scrubadub.detectors.PostalCodeDetector(locale='non_existant')

    def test_not_implemented_locale(self):
        """test a non existant region"""
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            with self.assertRaises(UserWarning):
                scrubadub.detectors.PostalCodeDetector(locale='fr_FR')

    def test_gb(self):
        """test a simple matching"""

        to_test = [
            # positive assertions
            ("BX1 1LT", True),
            ("sw1A 0AA", True),
            ("EC2V 7hh", True),
            ("M25DB", True),
            ("eh12ng", True),
            ("BT1 5GS", True),
            # negative assertions
            ("1", False),
            ("23", False),
            ("456", False),
            ("4567", False),
            ("750621", False),
            ("95130-642", False),
            ("95130-64212", False),
        ]

        test_str = 'this is a {} test string'
        detector = scrubadub.detectors.PostalCodeDetector(locale='en_GB')

        for postal_code, result in to_test:
            matches = list(detector.iter_filth(test_str.format(postal_code)))
            if result:
                self.assertEquals(len(matches), 1)
                self.assertEquals(matches[0].text, postal_code)
            else:
                self.assertEquals(matches, [])
