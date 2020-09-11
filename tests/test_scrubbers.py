import unittest

import scrubadub
from scrubadub.filth import MergedFilth, Filth


class ScrubberTestCase(unittest.TestCase):

    def test_clean_text(self):
        """make sure iter_filth doesn't fail with clean text"""
        text = 'the apple was eaten by a shark'
        scrubber = scrubadub.Scrubber()
        filths = [filth for filth in scrubber.iter_filth(text)]
        self.assertEqual(len(filths), 0)

    def test_filth_ordering(self):
        """make sure filth is returned in order"""
        scrubber = scrubadub.Scrubber()
        text = (
            "Alan can be reached by email alan@example.com or "
            "phone +1.312.456.6421"
        )
        order = []
        for filth in scrubber.iter_filth(text):
            order.append(filth.beg)
            order.append(filth.end)
        self.assertEqual(sorted(order), order)

    def test_filth_merge(self):
        """filth should merge properly"""
        # this looks like an email address 'me at john.doe' and skype
        text = "you can skype me at john.doe"
        scrubber = scrubadub.Scrubber()
        filths = [filth for filth in scrubber.iter_filth(text)]
        self.assertEqual(len(filths), 1)

    def test_filth_merge_placeholder(self):
        """filths should be merged into the biggest filth"""
        text = "you can skype me at john.doe"
        scrubber = scrubadub.Scrubber()
        for filth in scrubber.iter_filth(text):
            self.assertIsInstance(filth, MergedFilth)
            self.assertTrue('SKYPE' in filth.placeholder, filth.placeholder)
            self.assertTrue('EMAIL' in filth.placeholder, filth.placeholder)

    def test_add_duplicate_detector(self):
        """make sure adding a detector that already exists raises an error"""
        scrubber = scrubadub.Scrubber()
        with self.assertRaises(KeyError):
            scrubber.add_detector(scrubadub.detectors.email.EmailDetector)

    def test_add_non_detector(self):
        """make sure you can't add a detector that is not a Detector"""
        class NotDetector(object):
            pass

        scrubber = scrubadub.Scrubber()
        with self.assertRaises(TypeError):
            scrubber.add_detector(NotDetector)

    def test_add_detector_no_filth(self):
        """make sure you can't add a detector that is a Detector with a bad filth class"""
        class CleanDetector(scrubadub.detectors.Detector):
            filth_cls = object

        scrubber = scrubadub.Scrubber()
        with self.assertRaises(TypeError):
            scrubber.add_detector(CleanDetector)

    def test_iter_not_return_filth(self):
        """make sure a detector cant return non filth"""
        class FakeFilth(Filth):
            name = 'fakerfilth'

        class BadDetector(scrubadub.detectors.Detector):
            filth_cls = FakeFilth
            def iter_filth(self, text):
                yield 'Non-filth'

        scrubber = scrubadub.Scrubber()
        scrubber._detectors = {'fakerfilth': BadDetector}
        with self.assertRaises(TypeError):
            list(scrubber.iter_filth('A fake document with no pii'))
