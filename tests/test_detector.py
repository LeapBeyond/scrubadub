import unittest

from scrubadub.detectors.base import Detector, RegexDetector
from scrubadub.detectors.url import UrlDetector
from scrubadub.detectors.email import EmailDetector
from scrubadub.filth.base import Filth
from scrubadub.exceptions import UnexpectedFilth
import scrubadub


class DetectorTestCase(unittest.TestCase):
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

    def test_name_from_filth_cls(self):
        class OldFilth(Filth):
            type = 'old_filth'
        class OldDetector(Detector):
            filth_cls = OldFilth

        old_detector = OldDetector()
        self.assertEqual(old_detector.name, 'old_filth')

        detector = Detector()
        self.assertEqual(detector.name, 'detector')

    def test_abstract_detector_raises_error(self):
        """Test that the Detector abstract class raises an error when iter_filth is not implemented"""
        detector = Detector()
        with self.assertRaises(NotImplementedError):
            detector.iter_filth_documents(['text'], ['text.txt'])
        with self.assertRaises(NotImplementedError):
            detector.iter_filth('text')

    def test_abstract_regex_filth_raises_error(self):
        """Test that the RegexDetector abstract class raises an error when the filth_cls is incorrectly set"""
        class BadRegexDetector(RegexDetector):
            filth_cls = str

        detector = BadRegexDetector()
        with self.assertRaises(TypeError):
            list(detector.iter_filth('text'))

    def test_abstract_regex_raises_error(self):
        """Test that the RegexDetector abstract class raises an error when there is no regex set"""
        detector = RegexDetector()
        with self.assertRaises(ValueError):
            list(detector.iter_filth('text'))

    def test_non_detector_registration(self):
        """Test to ensure an error is raised if you try to register somthing thats not a detector"""

        detector = scrubadub.detectors.TwitterDetector()
        with self.assertRaises(ValueError):
            scrubadub.detectors.register_detector(detector, autoload=False)

        with self.assertRaises(ValueError):
            scrubadub.detectors.register_detector(123, autoload=False)

    def test_detector_registration(self):
        """Test to ensure adding a detector adds it to the configuration as expected"""

        class Temp(scrubadub.detectors.base.Detector):
            name = "temp"

        scrubadub.detectors.register_detector(Temp, autoload=False)

        self.assertIn(Temp.name, scrubadub.detectors.detector_configuration.keys())

        del scrubadub.detectors.detector_configuration[Temp.name]
