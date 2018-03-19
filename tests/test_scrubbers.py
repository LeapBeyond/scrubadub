import unittest

import scrubadub
from scrubadub.filth import MergedFilth


class ScrubberTestCase(unittest.TestCase):

    def test_clean_text(self):
        """make sure iter_filth_for_clean doesn't fail with clean text"""
        text = 'the apple was eaten by a shark'
        scrubber = scrubadub.Scrubber()
        filths = [filth for filth in scrubber.iter_filth_for_clean(text)]
        self.assertEqual(len(filths), 0)

    def test_filth_ordering(self):
        """make sure filth is returned in order"""
        scrubber = scrubadub.Scrubber()
        text = (
            "Alan can be reached by email alan@example.com or "
            "phone +1.312.456.6421"
        )
        order = []
        for filth in scrubber.iter_filth_for_clean(text):
            order.append(filth.beg)
            order.append(filth.end)
        self.assertEqual(sorted(order), order)

    def test_filth_merge(self):
        """filth should merge properly"""
        # this looks like an email address 'me at john.doe' and skype
        text = "you can skype me at john.doe"
        scrubber = scrubadub.Scrubber()
        filths = [filth for filth in scrubber.iter_filth_for_clean(text)]
        self.assertEqual(len(filths), 1)

    def test_filth_merge_placeholder(self):
        """filths should be merged into the biggest filth"""
        text = "you can skype me at john.doe"
        scrubber = scrubadub.Scrubber()
        for filth in scrubber.iter_filth_for_clean(text):
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
