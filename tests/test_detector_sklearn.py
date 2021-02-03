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

        token_test_cases = [
            (
                [(0, 5), (8, 10), (25, 26), ],
                ["B-ADD", "I-ADD", "I-ADD", ],
                {"minimum_ntokens": 1, "maximum_token_distance": 5, "b_token_required": False},
                (
                    [(0, 10), (25, 26), ],
                    ["ADD", "ADD", ],
                ),
            ),
            (
                [(0, 5), (8, 10), (25, 26), ],
                ["B-ADD", "I-ADD", "I-ADD", ],
                {"minimum_ntokens": 1, "maximum_token_distance": 20, "b_token_required": False},
                (
                    [(0, 26), ],
                    ["ADD", ],
                ),
            ),
            (
                [(0, 5), (8, 10), (25, 26), ],
                ["B-ADD", "I-ADD", "I-ADD", ],
                {"minimum_ntokens": 1, "maximum_token_distance": 4, "b_token_required": True},
                (
                    [(0, 10), ],
                    ["ADD", ],
                ),
            ),
            (
                [(0, 5), (8, 10), (25, 26), ],
                ["B-ADD", "I-ADD", "I-ADD", ],
                {"minimum_ntokens": 2, "maximum_token_distance": 4, "b_token_required": False},
                (
                    [(0, 10), ],
                    ["ADD", ],
                ),
            ),
            (
                [(0, 5), (8, 10), (25, 26), (28, 36), (50, 55), (58, 64), (80, 88), ],
                ["B-ADD", "I-ADD", "I-ADD", "I-ADD", "B-ADD", "I-ADD", "B-ADD", ],
                {"minimum_ntokens": 2, "maximum_token_distance": 4, "b_token_required": True},
                (
                    [(0, 10), (50, 64), ],
                    ["ADD", "ADD", ],
                ),
            ),
        ]

        for text_token_positions, text_labels, kwargs, test_result in token_test_cases:
            result = det._combine_iob_tokens(
                text_token_positions=text_token_positions,
                text_labels=text_labels,
                **kwargs
            )
            self.assertEqual(test_result, result)
