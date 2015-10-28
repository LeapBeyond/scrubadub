import unittest

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
