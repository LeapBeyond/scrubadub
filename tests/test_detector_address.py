import pandas as pd
import zipfile
import pathlib
import requests
import unittest
import warnings

import scrubadub

class AddressTestCase(unittest.TestCase):

    def setUp(self) -> None:
        import scrubadub.detectors.address

    def tearDown(self) -> None:
        if scrubadub.detectors.AddressDetector.name in scrubadub.detectors.detector_configuration:
            del scrubadub.detectors.detector_configuration[scrubadub.detectors.AddressDetector.name]

    def test_bad_locale(self):
        """test a non existant region"""
        with self.assertRaises(ValueError):
            scrubadub.detectors.AddressDetector(locale='non_existant')

    def test_not_implemented_locale(self):
        """test a non existant region"""
        scrubber = scrubadub.Scrubber(locale='fr_FR')
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            with self.assertRaises(UserWarning):
                scrubber.add_detector(scrubadub.detectors.AddressDetector)

    def test_gb(self):
        """test a simple matching"""

        to_test = [
            # positive assertions
            ("59 High Road, East Finchley London, N2 8AW", True),
            ("25 Fenchurch Avenue, London EC3M 5AD", True),
            ("12 Street Road, London N1P 2FZ", True),
            ("99 New London Road,\nChelmsford, CM2 0PP", True)
        ]

        test_str = 'this is a {} test string'
        detector = scrubadub.detectors.AddressDetector(locale='en_GB')

        for address, result in to_test:
            matches = list(detector.iter_filth(test_str.format(address)))
            if result:
                self.assertEquals(1, len(matches), "Unable to match " + address)
                self.assertEquals(matches[0].text, address)
            else:
                self.assertEquals(matches, [])
