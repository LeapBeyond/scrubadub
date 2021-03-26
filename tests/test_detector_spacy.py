import sys
import unittest

from scrubadub import Scrubber
from scrubadub.filth import NameFilth, OrganizationFilth, LocationFilth, Filth
from base import BaseTestCase


class SpacyDetectorTestCase(unittest.TestCase, BaseTestCase):
    """
    Tests whether the detector is performing correctly from a function point of view.
    For accuracy tests use .benchmark_accuracy instead
    """

    def setUp(self):
        unsupported_spacy_version = False
        try:
            from scrubadub.detectors.spacy import SpacyEntityDetector
            SpacyEntityDetector.check_spacy_version()
        except (ImportError, NameError):
            unsupported_spacy_version = True

        unsupported_python_version = (
                ((sys.version_info.major, sys.version_info.minor) < (3, 6)) 
        )
        if unsupported_python_version:
            self.skipTest(
                "Spacy detector supported for 3.6 <= python version"
            )
        elif unsupported_spacy_version:
            self.skipTest(
                "Need spacy version >= 3"
            )
        else:
            from scrubadub.detectors.spacy import SpacyEntityDetector
            self.detector = SpacyEntityDetector(model='en_core_web_sm')

    def _assert_filth_type_and_pos(self, doc_list, beg_end_list, filth_class):
        doc_names = [str(x) for x in range(len(doc_list))]

        filth_list = list(self.detector.iter_filth_documents(document_list=doc_list, document_names=doc_names))

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
        beg_end_list = [(24, 29),
                        (21, 27)]

        self._assert_filth_type_and_pos(doc_list, beg_end_list, OrganizationFilth)

    def test_location(self):
        self.detector.named_entities = {"GPE"}
        doc_list = ["London is a city in England"]
        beg_end_list = [(0, 6),
                        (20, 27)]

        self._assert_filth_type_and_pos(doc_list, beg_end_list, LocationFilth)

    def test_unknown_entity(self):
        self.detector.named_entities = {"PERCENT"}
        doc_list = ["20% of the city is in ruins."]
        beg_end_list = [(0, 3)]

        self._assert_filth_type_and_pos(doc_list, beg_end_list, Filth)

    def test_wrong_model(self):
        """Test that it raises an error if user inputs invalid spacy model"""
        from scrubadub.detectors.spacy import SpacyEntityDetector
        with self.assertRaises(SystemExit):
            SpacyEntityDetector(model='not_a_valid_spacy_model')

    def test_iter_filth(self):
        doc = "John is a cat"

        output_iter_docs = list(self.detector.iter_filth_documents(document_list=[doc], document_names=["0"]))
        output_iter = list(self.detector.iter_filth(text=doc, document_name="0"))

        self.assertListEqual(output_iter, output_iter_docs)

    def test_compatibility_with_scrubber(self):
        doc_list = ["John is a cat",
                    "When was Maria born?"]
        result = ["{{NAME}} is a cat",
                  "When was {{NAME}} born?"]

        s = Scrubber(detector_list=[self.detector])

        clean_docs = s.clean_documents(documents=doc_list)
        self.assertIsInstance(clean_docs, list)
        self.assertListEqual(result, clean_docs)

    def test_long_text(self):
        # The transformer cant take text with many spaces as his creates many tokens and there is a limit to the
        # width of the transformer in the model.
        from scrubadub.detectors.spacy import SpacyEntityDetector
        for whitespace in [' ', '\t', '\n']:
            longtext = (whitespace * 20).join(['asd', 'qwe', 'Mike', '']) * 10
            detector = SpacyEntityDetector(model='en_core_web_trf')
            filths = list(detector.iter_filth(longtext))
            self.assertIsInstance(filths, list)
            self.assertEqual(len(filths), 10)
            self.assertEqual(filths[-1].beg, len(longtext)-20-4)
            self.assertEqual(filths[-1].end, len(longtext)-20)
