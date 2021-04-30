import unittest

import scrubadub

class PredefinedTestCase(unittest.TestCase):

    def test_simple(self):
        """test a simple matching"""

        test_str = 'this is a test string'
        detector = scrubadub.detectors.TaggedEvaluationFilthDetector([
            {'match': 'test', 'filth_type': 'test'},
        ])

        matches = list(detector.iter_filth(test_str))
        self.assertEqual(matches[0].beg, 10)
        self.assertEqual(matches[0].end, 14)

    def test_ignore_case(self):
        """test a matching, ignoring case"""

        test_str = 'this is a test string'
        detector = scrubadub.detectors.TaggedEvaluationFilthDetector([
            {'match': 'Test', 'filth_type': 'test', 'ignore_case': True},
        ])

        matches = list(detector.iter_filth(test_str))
        self.assertEqual(10, matches[0].beg)
        self.assertEqual(14, matches[0].end)

        detector = scrubadub.detectors.TaggedEvaluationFilthDetector([
            {'match': 'Test', 'filth_type': 'test', 'ignore_case': False},
        ])

        matches = list(detector.iter_filth(test_str))
        self.assertEqual(0, len(matches))

    def test_ignore_whitespace(self):
        """test a matching, ignoring whitespace"""

        test_str = 'this\n is\t  a test  string'
        detector = scrubadub.detectors.TaggedEvaluationFilthDetector([
            {'match': 'this is a \n\n\ntest', 'filth_type': 'test', 'ignore_whitespace': True},
        ])

        matches = list(detector.iter_filth(test_str))
        self.assertEqual(1, len(matches))
        self.assertEqual(0, matches[0].beg)
        self.assertEqual(17, matches[0].end)

        detector = scrubadub.detectors.TaggedEvaluationFilthDetector([
            {'match': 'this is a \n\n\ntest', 'filth_type': 'test', 'ignore_whitespace': False},
        ])

        matches = list(detector.iter_filth(test_str))
        self.assertEqual(0, len(matches))

    def test_ignore_partial_match(self):
        """test a matching, ignoring whitespace"""

        test_str = 'this is a test string'
        detector = scrubadub.detectors.TaggedEvaluationFilthDetector([
            {'match': 'is', 'filth_type': 'test', 'ignore_partial_word_matches': True},
        ])

        matches = list(detector.iter_filth(test_str))
        self.assertEqual(1, len(matches))
        self.assertEqual(5, matches[0].beg)
        self.assertEqual(7, matches[0].end)

        detector = scrubadub.detectors.TaggedEvaluationFilthDetector([
            {'match': 'is', 'filth_type': 'test', 'ignore_partial_word_matches': False},
        ])

        matches = list(detector.iter_filth(test_str))
        self.assertEqual(2, len(matches))
        self.assertEqual(2, matches[0].beg)
        self.assertEqual(4, matches[0].end)
        self.assertEqual(5, matches[1].beg)
        self.assertEqual(7, matches[1].end)

    def test_empty(self):
        """test a simple matching"""

        test_str = 'this is a test string'

        detector = scrubadub.detectors.TaggedEvaluationFilthDetector([])
        matches = list(detector.iter_filth(test_str))
        self.assertEqual(len(matches), 0)

    def test_wrong_types(self):
        with self.assertRaises(ValueError):
            scrubadub.detectors.TaggedEvaluationFilthDetector([
                {'match': 1234, 'filth_type': 'test', 'ignore_case': True},
            ])
        with self.assertRaises(ValueError):
            scrubadub.detectors.TaggedEvaluationFilthDetector([
                {'match': '1234', 'filth_type': 1234, 'ignore_case': True},
            ])
        with self.assertRaises(ValueError):
            scrubadub.detectors.TaggedEvaluationFilthDetector([
                {'match': '1234', 'filth_type': '1234', 'match_end': 1234, 'ignore_case': True},
            ])

    def test_start_end(self):
        """text matches with a start and end"""

        test_str = 'hello this is a test string'
        detector = scrubadub.detectors.TaggedEvaluationFilthDetector([
            {'match': 'this is', 'match_end': 'test', 'filth_type': 'test'},
        ])

        matches = list(detector.iter_filth(test_str))
        self.assertEqual(matches[0].beg, 6)
        self.assertEqual(matches[0].end, 20)

    def test_word_boundaires(self):
        """test that word boundaries work as expected"""

        test_str = 'hello this is a test string'
        detector = scrubadub.detectors.TaggedEvaluationFilthDetector([
            {'match': 'is', 'filth_type': 'test', 'ignore_partial_word_matches': False},
        ])
        matches = list(detector.iter_filth(test_str))

        self.assertEqual(matches[0].beg, 8)
        self.assertEqual(matches[0].end, 10)
        self.assertEqual(matches[1].beg, 11)
        self.assertEqual(matches[1].end, 13)
        self.assertEqual(len(matches), 2)

        detector = scrubadub.detectors.TaggedEvaluationFilthDetector([
            {'match': 'is', 'filth_type': 'test', 'ignore_partial_word_matches': True},
        ])
        matches = list(detector.iter_filth(test_str))

        self.assertEqual(matches[0].beg, 11)
        self.assertEqual(matches[0].end, 13)
        self.assertEqual(len(matches), 1)

    def test_text_case(self):
        """test that word boundaries work as expected"""

        test_str = 'hello this is a test string'
        detector = scrubadub.detectors.TaggedEvaluationFilthDetector([
            {'match': 'This', 'filth_type': 'test', 'ignore_case': True},
        ])
        matches = list(detector.iter_filth(test_str))

        self.assertEqual(matches[0].beg, 6)
        self.assertEqual(matches[0].end, 10)
        self.assertEqual(len(matches), 1)

        detector = scrubadub.detectors.TaggedEvaluationFilthDetector([
            {'match': 'This', 'filth_type': 'test', 'ignore_case': False},
        ])
        matches = list(detector.iter_filth(test_str))
        self.assertEqual(len(matches), 0)

    def test_start_no_end(self):
        """text matches with a start and an invalid end"""

        test_str = 'hello this is a test string'
        detector = scrubadub.detectors.TaggedEvaluationFilthDetector([
            {'match': 'this is', 'match_end': 'impossible to find', 'filth_type': 'test'},
        ])

        matches = list(detector.iter_filth(test_str))
        self.assertEqual(len(matches), 0)

    def test_error(self):
        """text exceptions thrown by predefined"""

        with self.assertRaises(KeyError):
            detector = scrubadub.detectors.TaggedEvaluationFilthDetector([
                {'non_existiant': 'this is'},
            ])

        with self.assertRaises(KeyError):
            detector = scrubadub.detectors.TaggedEvaluationFilthDetector([
                {'match': 'the match', 'filth_type': 'email', 'non_existiant': 'this is'},
            ])

    def test_filth_string(self):
        filth = scrubadub.filth.TaggedEvaluationFilth(beg=0, end=5)
        self.assertEqual(str(filth), "<TaggedEvaluationFilth text='' beg=0 end=5>")

        filth = scrubadub.filth.TaggedEvaluationFilth(beg=0, end=5, text='hello')
        self.assertEqual(str(filth), "<TaggedEvaluationFilth text='hello' beg=0 end=5>")

        filth = scrubadub.filth.TaggedEvaluationFilth(beg=0, end=5, text='hello', document_name='hello.txt')
        self.assertEqual(str(filth), "<TaggedEvaluationFilth text='hello' document_name='hello.txt' beg=0 end=5>")

        filth = scrubadub.filth.TaggedEvaluationFilth(beg=0, end=5, text='hello', comparison_type='greeting')
        self.assertEqual(str(filth), "<TaggedEvaluationFilth text='hello' beg=0 end=5 comparison_type='greeting'>")

        filth = scrubadub.filth.TaggedEvaluationFilth(beg=0, end=5, text='hello', document_name='hello.txt',
                                                      comparison_type='greeting')
        self.assertEqual(
            str(filth),
            "<TaggedEvaluationFilth text='hello' document_name='hello.txt' beg=0 end=5 comparison_type='greeting'>"
        )
