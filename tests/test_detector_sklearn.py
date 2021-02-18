import unittest

import scrubadub.detectors.sklearn_address
from scrubadub.detectors.base import Detector, RegexDetector
from scrubadub.detectors.url import UrlDetector
from scrubadub.detectors.email import EmailDetector
from scrubadub.filth.base import Filth
from scrubadub.exceptions import UnexpectedFilth
import scrubadub


class SklearnTestCase(unittest.TestCase):

    def setUp(self) -> None:
        import scrubadub.detectors.sklearn
        scrubadub.detectors.register_detector(scrubadub.detectors.sklearn_address.SklearnAddressDetector)

    def tearDown(self) -> None:
        import scrubadub.detectors.sklearn
        del scrubadub.detectors.detector_configuration[scrubadub.detectors.sklearn_address.SklearnAddressDetector.name]

    def test_combine_tokens(self):
        """ensure that tokens are correctly combined"""

        import scrubadub.detectors.sklearn
        det = scrubadub.detectors.sklearn.BIOTokenSklearnDetector()

        from scrubadub.detectors.sklearn import TokenTupleWithLabel, TokenPosition

        text = 'Card well protect drug professor now.\nInside present right both. Computer prepare style whose ' \
               'business including big.'

        token_test_cases = [
            (
                [
                    TokenTupleWithLabel('a.txt', text[0:5], TokenPosition(0, 5), 'B-ADD'),
                    TokenTupleWithLabel('a.txt', text[8:10], TokenPosition(8, 10), 'I-ADD'),
                    TokenTupleWithLabel('a.txt', text[25:26], TokenPosition(25, 26), 'I-ADD'),
                ],
                {
                    "document_list": [text],
                    "document_names": ['a.txt'],
                    "minimum_ntokens": 1,
                    "number_missing_tokens_allowed": None,
                    "number_missing_characters_allowed": 5,
                    "b_token_required": True,
                },
                [
                    TokenTupleWithLabel('a.txt', text[0:10], TokenPosition(0, 10), 'ADD'),
                ],
            ),
            (
                [
                    TokenTupleWithLabel('a.txt', text[0:5], TokenPosition(0, 5), 'B-ADD'),
                    TokenTupleWithLabel('a.txt', text[8:10], TokenPosition(8, 10), 'I-ADD'),
                    TokenTupleWithLabel('a.txt', text[25:26], TokenPosition(25, 26), 'I-ADD'),
                ],
                {
                    "document_list": [text],
                    "document_names": ['a.txt'],
                    "minimum_ntokens": 1,
                    "number_missing_tokens_allowed": None,
                    "number_missing_characters_allowed": 20,
                    "b_token_required": False,
                },
                [
                    TokenTupleWithLabel('a.txt', text[0:26], TokenPosition(0, 26), 'ADD'),
                ],
            ),
            (
                [
                    TokenTupleWithLabel('a.txt', text[0:5], TokenPosition(0, 5), 'B-ADD'),
                    TokenTupleWithLabel('a.txt', text[8:10], TokenPosition(8, 10), 'I-ADD'),
                    TokenTupleWithLabel('a.txt', text[25:26], TokenPosition(25, 26), 'I-ADD'),
                ],
                {
                    "document_list": [text],
                    "document_names": ['a.txt'],
                    "minimum_ntokens": 1,
                    "number_missing_tokens_allowed": None,
                    "number_missing_characters_allowed": 4,
                    "b_token_required": True,
                },
                [
                    TokenTupleWithLabel('a.txt', text[0:10], TokenPosition(0, 10), 'ADD'),
                ],
            ),
            (
                [
                    TokenTupleWithLabel('a.txt', text[0:5], TokenPosition(0, 5), 'B-ADD'),
                    TokenTupleWithLabel('a.txt', text[8:10], TokenPosition(8, 10), 'I-ADD'),
                    TokenTupleWithLabel('a.txt', text[25:26], TokenPosition(25, 26), 'I-ADD'),
                ],
                {
                    "document_list": [text],
                    "document_names": ['a.txt'],
                    "minimum_ntokens": 2,
                    "number_missing_tokens_allowed": None,
                    "number_missing_characters_allowed": 4,
                    "b_token_required": False,
                },
                [
                    TokenTupleWithLabel('a.txt', text[0:10], TokenPosition(0, 10), 'ADD'),
                ],
            ),
            (
                [
                    TokenTupleWithLabel('a.txt', text[0:5], TokenPosition(0, 5), 'B-ADD'),
                    TokenTupleWithLabel('a.txt', text[8:10], TokenPosition(8, 10), 'I-ADD'),
                    TokenTupleWithLabel('a.txt', text[12:15], TokenPosition(12, 15), 'O'),
                    TokenTupleWithLabel('a.txt', text[16:17], TokenPosition(16, 17), 'O'),
                    TokenTupleWithLabel('a.txt', text[25:27], TokenPosition(25, 27), 'I-ADD'),
                ],
                {
                    "document_list": [text],
                    "document_names": ['a.txt'],
                    "minimum_ntokens": 1,
                    "number_missing_tokens_allowed": 0,
                    "number_missing_characters_allowed": None,
                    "b_token_required": False,
                },
                [
                    TokenTupleWithLabel('a.txt', text[0:10], TokenPosition(0, 10), 'ADD'),
                    TokenTupleWithLabel('a.txt', text[25:27], TokenPosition(25, 27), 'ADD'),
                ],
            ),
            (
                [
                    TokenTupleWithLabel('a.txt', text[0:5], TokenPosition(0, 5), 'B-ADD'),
                    TokenTupleWithLabel('a.txt', text[8:10], TokenPosition(8, 10), 'I-ADD'),
                    TokenTupleWithLabel('a.txt', text[12:15], TokenPosition(11, 14), 'O'),
                    TokenTupleWithLabel('a.txt', text[16:17], TokenPosition(15, 17), 'I-ADD'),
                ],
                {
                    "document_list": [text],
                    "document_names": ['a.txt'],
                    "minimum_ntokens": 2,
                    "number_missing_tokens_allowed": 0,
                    "number_missing_characters_allowed": 6,
                    "b_token_required": False,
                },
                [
                    TokenTupleWithLabel('a.txt', text[0:10], TokenPosition(0, 10), 'ADD'),
                ],
            ),
            (
                [
                    TokenTupleWithLabel('a.txt', text[0:5], TokenPosition(0, 5), 'B-ADD'),
                    TokenTupleWithLabel('a.txt', text[8:10], TokenPosition(8, 10), 'I-ADD'),
                    TokenTupleWithLabel('a.txt', text[12:15], TokenPosition(11, 14), 'O'),
                    TokenTupleWithLabel('a.txt', text[16:17], TokenPosition(15, 17), 'I-ADD'),
                ],
                {
                    "document_list": [text],
                    "document_names": ['a.txt'],
                    "minimum_ntokens": 2,
                    "number_missing_tokens_allowed": 1,
                    "number_missing_characters_allowed": 3,
                    "b_token_required": False,
                },
                [
                    TokenTupleWithLabel('a.txt', text[0:10], TokenPosition(0, 10), 'ADD'),
                ],
            ),
            (
                [
                    TokenTupleWithLabel('a.txt', text[0:5], TokenPosition(0, 5), 'B-ADD'),
                    TokenTupleWithLabel('a.txt', text[8:10], TokenPosition(8, 10), 'I-ADD'),
                    TokenTupleWithLabel('a.txt', text[12:15], TokenPosition(11, 14), 'O'),
                    TokenTupleWithLabel('a.txt', text[16:17], TokenPosition(15, 17), 'I-ADD'),
                ],
                {
                    "document_list": [text],
                    "document_names": ['a.txt'],
                    "minimum_ntokens": 2,
                    "number_missing_tokens_allowed": 1,
                    "number_missing_characters_allowed": 6,
                    "b_token_required": False,
                },
                [
                    TokenTupleWithLabel('a.txt', text[0:17], TokenPosition(0, 17), 'ADD'),
                ],
            ),
            (
                [
                    TokenTupleWithLabel('a.txt', text[0:5], TokenPosition(0, 5), 'B-ADD'),
                    TokenTupleWithLabel('a.txt', text[8:10], TokenPosition(8, 10), 'I-ADD'),
                    TokenTupleWithLabel('a.txt', text[12:15], TokenPosition(12, 15), 'O'),
                    TokenTupleWithLabel('a.txt', text[16:17], TokenPosition(16, 17), 'O'),
                    TokenTupleWithLabel('a.txt', text[25:26], TokenPosition(25, 26), 'I-ADD'),
                ],
                {
                    "document_list": [text],
                    "document_names": ['a.txt'],
                    "minimum_ntokens": 1,
                    "number_missing_tokens_allowed": 2,
                    "number_missing_characters_allowed": None,
                    "b_token_required": False,
                },
                [
                    TokenTupleWithLabel('a.txt', text[0:26], TokenPosition(0, 26), 'ADD'),
                ],
            ),
            (
                [
                    TokenTupleWithLabel('a.txt', text[0:5], TokenPosition(0, 5), 'B-ADD'),
                    TokenTupleWithLabel('a.txt', text[8:10], TokenPosition(8, 10), 'I-ADD'),
                    TokenTupleWithLabel('a.txt', text[25:26], TokenPosition(25, 26), 'I-ADD'),
                    TokenTupleWithLabel('a.txt', text[28:36], TokenPosition(28, 36), 'I-ADD'),
                    TokenTupleWithLabel('a.txt', text[50:55], TokenPosition(50, 55), 'B-ADD'),
                    TokenTupleWithLabel('a.txt', text[58:64], TokenPosition(58, 64), 'I-ADD'),
                    TokenTupleWithLabel('a.txt', text[80:88], TokenPosition(80, 88), 'I-ADD'),
                ],
                {
                    "document_list": [text],
                    "document_names": ['a.txt'],
                    "minimum_ntokens": 2,
                    "number_missing_tokens_allowed": None,
                    "number_missing_characters_allowed": 4,
                    "b_token_required": True,
                },
                [
                    TokenTupleWithLabel('a.txt', text[0:10], TokenPosition(0, 10), 'ADD'),
                    TokenTupleWithLabel('a.txt', text[50:64], TokenPosition(50, 64), 'ADD'),
                ],
            ),
        ]

        for tokens, kwargs, test_result in token_test_cases:
            result = det._combine_iob_tokens(
                text_tokens=tokens,
                **kwargs
            )
            self.assertEqual(test_result, result)
