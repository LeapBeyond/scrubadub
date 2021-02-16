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
            from scrubadub.detectors.spacy_expand_person_title import SpacyExpandPersonTitle
            SpacyExpandPersonTitle.check_spacy_version()
        except (ImportError, NameError):
            unsupported_spacy_version = True

        unsupported_python_version = (
                ((sys.version_info.major, sys.version_info.minor) < (3, 6)) or
                ((sys.version_info.major, sys.version_info.minor) >= (3, 9))
        )
        print("HERE")
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
            from scrubadub.detectors.spacy_expand_person_title import SpacyExpandPersonTitle
            self.detector = SpacyExpandPersonTitle(model='en_core_web_sm')

    def _assert_filth_type_and_pos(self, doc_list, beg_end_list, filth_class):
        doc_names = [str(x) for x in range(len(doc_list))]

        filth_list = list(self.detector.iter_filth_documents(document_list=doc_names, document_names=doc_list))

        for filth, beg_end in zip(filth_list, beg_end_list):
            self.assertIsInstance(filth, filth_class)
            self.assertEqual((filth.beg, filth.end), beg_end)

    def test_expand_names(self):
        doc_list = ["Mr Nadhim Zahawi said the measures would help our economy.",
                    "The name is Mrs Nasrin Muhib.",
                    "Can you please ask Mr lan Chase?",
                    "Please see Dr Alex Smith in room 1."]
        beg_end_list = [(0, 16),
                        (12, 28),
                        (19, 31),
                        (11, 24)]
        self._assert_filth_type_and_pos(doc_list, beg_end_list, NameFilth)
