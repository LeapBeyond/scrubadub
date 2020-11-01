import sys
import unittest

from scrubadub.detectors import NamedEntityDetector
from scrubadub.filth import NameFilth, OrganizationFilth, NamedEntityFilth
from base import BaseTestCase


class NamedEntityTestCase(unittest.TestCase, BaseTestCase):
    """
    Tests whether the detector is performing correctly from a function point of view.
    For accuracy tests use .benchmark_accuracy instead
    """

    def setUp(self):
        unsupported_version = (sys.version_info.major, sys.version_info.minor) < (3, 6)
        unittest.TestCase.skipTest(
            unsupported_version,
            "Named entity detector not supported for python<3.6"
        )
        if not unsupported_version:
            self.detector = NamedEntityDetector()

    def _assert_filth_type_and_pos(self, doc_list, beg_end_list, filth_class):
        doc_names = [str(x) for x in range(len(doc_list))]

        filth_list = list(self.detector.iter_filth_documents(doc_names, doc_list))

        for filth, beg_end in zip(filth_list, beg_end_list):
            self.assertIsInstance(filth, filth_class)
            self.assertEqual((filth.beg, filth.end), beg_end)

    def test_names(self):
        doc_list = ["John is a cat",
                    "When was Maria born?",
                    "john is a cat",
                    "when was maria born"]
        beg_end_list = [(0, 4),
                        (9, 14),
                        (0, 4),
                        (9, 14)]

        self._assert_filth_type_and_pos(doc_list, beg_end_list, NameFilth)

    def test_organisations(self):
        doc_list = ["She started working for Apple this year",
                    "But used to work for Google"]
        beg_end_list = [(24, 30),
                        (21, 27)]

        self._assert_filth_type_and_pos(doc_list, beg_end_list, OrganizationFilth)

    def test_other_entity(self):
        self.detector.named_entities = {"GPE"}
        doc_list = ["London is a city in England"]
        beg_end_list = [(0, 6),
                        (20, 27)]

        self._assert_filth_type_and_pos(doc_list, beg_end_list, NamedEntityFilth)

    def test_wrong_model(self):
        """Test that it raises an error if user inputs invalid spacy model"""
        with self.assertRaises(SystemExit):
            NamedEntityDetector(model='not_a_valid_spacy_model')

    def test_iter_filth(self):
        doc = "John is a cat"

        output_iter_docs = list(self.detector.iter_filth_documents(doc_list=[doc], doc_names=["0"]))
        output_iter = list(self.detector.iter_filth(text=doc, document_name="0"))

        self.assertListEqual(output_iter, output_iter_docs)
