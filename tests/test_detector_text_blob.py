import unittest

from base import BaseTestCase

import scrubadub

class TextBlobNameTestCase(unittest.TestCase, BaseTestCase):

    def setUp(self):
        from scrubadub.detectors.text_blob import TextBlobNameDetector
        scrubadub.detectors.register_detector(TextBlobNameDetector, autoload=True)

    def test_john(self):
        """
        BEFORE: John is a cat
        AFTER:  {{NAME}} is a cat
        """
        self.compare_before_after()

    def test_no_names(self):
        """
        BEFORE: Hello. Please testing.
        AFTER: Hello. Please testing.
        """
        self.compare_before_after()

    @unittest.skip('lower names cause problems for textblob')
    def test_lower_names(self):
        """
        BEFORE: sarah is a friendly person
        AFTER: {{NAME}} is a friendly person
        """
        self.compare_before_after()

    def test_disallowed_nouns(self):
        import scrubadub.detectors.text_blob
        detector = scrubadub.detectors.text_blob.TextBlobNameDetector()
        detector.disallowed_nouns = set()
        with self.assertRaises(TypeError):
            list(detector.iter_filth('John is a cat'))

    def tearDown(self) -> None:
        from scrubadub.detectors.text_blob import TextBlobNameDetector
        del scrubadub.detectors.detector_configuration[TextBlobNameDetector.name]
