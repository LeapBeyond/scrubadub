import unittest

from scrubadub.detectors.known import KnownFilthDetector

class PredefinedTestCase(unittest.TestCase):

    def test_simple(self):
        """test a simple matching"""

        test_str = 'this is a test string'
        detector = KnownFilthDetector([
            {'match': 'test'},
        ])

        matches = list(detector.iter_filth(test_str))
        self.assertEquals(matches[0].beg, 10)
        self.assertEquals(matches[0].end, 14)

    def test_start_end(self):
        """text matches with a start and end"""

        test_str = 'hello this is a test string'
        detector = KnownFilthDetector([
            {'start': 'this is', 'end': 'test'},
        ])

        matches = list(detector.iter_filth(test_str))
        self.assertEquals(matches[0].beg, 6)
        self.assertEquals(matches[0].end, 20)

    def test_error(self):
        """text exceptions thrown by predefined"""

        test_str = 'hello this is a test string'
        detector = KnownFilthDetector([
            {'non_existiant': 'this is', 'items': 'test'},
        ])

        with self.assertRaises(ValueError):
            list(detector.iter_filth(test_str))