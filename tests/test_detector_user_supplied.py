import unittest

import scrubadub

class UserDefinedTestCase(unittest.TestCase):

    def test_simple(self):
        """test a simple matching"""

        test_str = 'this is a test string'
        detector = scrubadub.detectors.UserSuppliedFilthDetector([
            {'match': 'test', 'filth_type': 'name'},
        ])

        matches = list(detector.iter_filth(test_str))
        self.assertEqual(matches[0].beg, 10)
        self.assertEqual(matches[0].end, 14)

    def test_bad_filth(self):
        """test a simple matching"""

        test_str = 'this is a test string'
        detector = scrubadub.detectors.UserSuppliedFilthDetector([
            {'match': 'test', 'filth_type': 'invalid_filth'},
        ])

        with self.assertRaises(KeyError):
            list(detector.iter_filth(test_str))
