import unittest

import scrubadub
from scrubadub.detectors.url import UrlDetector
from scrubadub.detectors.email import EmailDetector


class DetectorTestCase(unittest.TestCase):
    pass
    # TODO: test detector names

    def test_detector_names(self):
        """make sure detector names appear in Filth"""
        detector = UrlDetector(name='example_name')
        filths = list(detector.iter_filth('www.google.com'))
        self.assertEqual(len(filths), 1)
        self.assertEqual(filths[0].detector_name, 'example_name')

        detector = EmailDetector(name='example_name')
        filths = list(detector.iter_filth('example@example.com'))
        self.assertEqual(len(filths), 1)
        self.assertEqual(filths[0].detector_name, 'example_name')

