import unittest
import warnings

import scrubadub
import scrubadub.utils

class OldAPITestCase(unittest.TestCase):

    def setUp(self):
        from scrubadub.detectors.text_blob import TextBlobNameDetector
        scrubadub.detectors.register_detector(TextBlobNameDetector, autoload=True)

    def test_scrubadub_clean(self):
        """test old scrubadub API"""
        text = u"John is a cat"
        self.assertEqual(
            scrubadub.clean(text),
            "{{NAME}} is a cat",
        )

        scrubadub.filth.Filth.lookup = scrubadub.utils.Lookup()
        with warnings.catch_warnings(record=True) as warning_context:
            warnings.simplefilter("always")
            try:
                self.assertEqual(
                    scrubadub.clean(text, replace_with='identifier'),
                    "{{NAME-0}} is a cat",
                )
            finally:
                warnings.simplefilter("default")
            self.assertTrue(sum(issubclass(w.category, DeprecationWarning) for w in warning_context) > 0)


        scrubadub.filth.Filth.lookup = scrubadub.utils.Lookup()
        with warnings.catch_warnings(record=True) as warning_context:
            warnings.simplefilter("always")
            try:
                self.assertEqual(
                    scrubadub.clean("John spoke with Doug.", replace_with='identifier'),
                    "{{NAME-0}} spoke with {{NAME-1}}.",
                )
            finally:
                warnings.simplefilter("default")
            self.assertTrue(sum(issubclass(w.category, DeprecationWarning) for w in warning_context) > 0)

        scrubadub.filth.Filth.lookup = scrubadub.utils.Lookup()

    def test_scrubber_clean(self):
        """test older scrubber API"""
        scrubber = scrubadub.Scrubber()
        scrubber.remove_detector('email')
        text = "contact Joe Duffy at joe@example.com"
        self.assertEqual(
            scrubadub.clean(text),
            "contact {{NAME}} {{NAME}} at {{EMAIL}}",
        )

    def test_filth_class(self):
        class MyFilth(scrubadub.filth.Filth):
            type = 'mine'

        class MyDetector(scrubadub.detectors.Detector):
            filth_cls = MyFilth

            def iter_filth(self, text, **kwargs):
               yield MyFilth(beg=0, end=8, text='My stuff', **kwargs)

        scrubber = scrubadub.Scrubber()
        # TODO: Add depreciation warning
        scrubber.add_detector(MyDetector)
        text = "My stuff can be found there."

        self.assertEqual(
            scrubber.clean(text),
            "{{MINE}} can be found there.",
        )

    def test_filth_markers(self):
        prefix = scrubadub.filth.base.Filth.prefix
        suffix = scrubadub.filth.base.Filth.suffix
        scrubadub.filth.base.Filth.prefix = '<b>'
        scrubadub.filth.base.Filth.suffix = '</b>'

        scrubber = scrubadub.Scrubber()

        with warnings.catch_warnings(record=True) as warning_context:
            warnings.simplefilter("always")
            try:
                self.assertEqual(
                    scrubber.clean("contact Joe Duffy at joe@example.com"),
                    "contact <b>NAME</b> <b>NAME</b> at <b>EMAIL</b>",
                )
            finally:
                warnings.simplefilter("default")
                # Ensure that this is reset, no matter what happens above
                scrubadub.filth.base.Filth.prefix = prefix
                scrubadub.filth.base.Filth.suffix = suffix
            self.assertTrue(sum(issubclass(w.category, DeprecationWarning) for w in warning_context) > 0)

    def test_regex_filth(self):
        """Test for a DeprecationWarning when using RegexFilth."""
        with warnings.catch_warnings(record=True) as warning_context:
            warnings.simplefilter("always")
            try:
                scrubadub.filth.RegexFilth(0, 2, 'ab')
            finally:
                warnings.simplefilter("default")
            self.assertEqual(sum(issubclass(w.category, DeprecationWarning) for w in warning_context), 1)

    def tearDown(self) -> None:
        from scrubadub.detectors.text_blob import TextBlobNameDetector
        del scrubadub.detectors.detector_configuration[TextBlobNameDetector.name]
