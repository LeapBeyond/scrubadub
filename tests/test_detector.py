import unittest

import scrubadub
from scrubadub.detectors.base import RegexDetector
from scrubadub.filth.base import Filth
from scrubadub.exceptions import UnexpectedFilth


class RegexDetectorTestCase(unittest.TestCase):

    def test_regex_filth(self):
        """make sure RegexDetector only works with RegexFilth"""

        class MyFilth(Filth):
            pass

        class MyDetector(RegexDetector):
            filth_cls = MyFilth

        text = 'dirty dirty text'
        detector = MyDetector()
        with self.assertRaises(UnexpectedFilth):
            for filth in detector.iter_filth(text):
                pass

    def test_detector_filth_cls(self):
        """Detector.filth_cls should always exist"""
        for detector_cls in scrubadub.detectors.iter_detectors():
            self.assertTrue(getattr(detector_cls, 'filth_cls', False),
                '%s does not have a filth_cls set' % detector_cls
            )
