import sys
import unittest

from scrubadub.filth import NameFilth
from base import BaseTestCase


class SpacyExpandPersonTitleTestCase(unittest.TestCase, BaseTestCase):
    """
    Tests whether the detector is performing correctly from a function point of view.
    For accuracy tests use .benchmark_accuracy instead
    """

    def setUp(self):
        unsupported_spacy_version = False
        try:
            from scrubadub.detectors.spacy_name_title import SpacyNameTitleDetector
            SpacyNameTitleDetector.check_spacy_version()
        except (ImportError, NameError):
            unsupported_spacy_version = True

        unsupported_python_version = (
                ((sys.version_info.major, sys.version_info.minor) < (3, 6)) or
                ((sys.version_info.major, sys.version_info.minor) >= (3, 9))
        )
        if unsupported_python_version:
            print("SKIPPED")
            self.skipTest(
                "Spacy detector supported for 3.6 <= python version < 3.9"
            )
        elif unsupported_spacy_version:
            self.skipTest(
                "Need spacy version >= 3"
            )
        else:
            from scrubadub.detectors.spacy_name_title import SpacyNameTitleDetector
            self.detector = SpacyNameTitleDetector()

    def test_expand_names(self):
        doc_list = [
            "Mr Jake Doe said the measures would help our economy.",
            "The name is Mrs Nasrin Muhib.",
            "Can you please ask Mr lan Chase?",
            "Please see Dr Alex Smith in room 1."
        ]
        beg_end_list = [
            (0, 11),
            (12, 28),
            (19, 31),
            (11, 24)
        ]
        for doc, beg_end in zip(doc_list, beg_end_list):
            filth_list = list(self.detector.iter_filth(doc))
            print(filth_list)
            self.assertLessEqual(1, len(filth_list), doc)
            self.assertIsInstance(filth_list[0], NameFilth, doc)
            self.assertEqual((filth_list[0].beg, filth_list[0].end), beg_end, doc)
