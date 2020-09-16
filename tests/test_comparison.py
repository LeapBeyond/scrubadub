import unittest

import scrubadub
import scrubadub.comparison
from scrubadub.filth.base import MergedFilth, Filth
from scrubadub.filth.phone import PhoneFilth
from scrubadub.filth.known import KnownFilth
from scrubadub.detectors.base import Detector
from scrubadub.detectors.phone import PhoneDetector
from scrubadub.detectors.known import KnownFilthDetector

class ComparisonTestCase(unittest.TestCase):

    def test_comparison(self):
        """test basic comparison"""
        filths = [
            MergedFilth(
                PhoneFilth(beg=0, end=4, text='1234'),
                KnownFilth(beg=0, end=4, text='1234', comparison_type='phone'),
            ),
            KnownFilth(beg=5, end=10, text='12345', comparison_type='phone'),
            MergedFilth(
                PhoneFilth(beg=5, end=9, text='1234'),
                KnownFilth(beg=5, end=9, text='1234', comparison_type='phone'),
            ),
            KnownFilth(beg=15, end=20, text='12345', comparison_type='phone'),
        ]

        self.assertEquals(
            scrubadub.comparison.compare_detectors_to_known_types(
                filths,
                [PhoneDetector, KnownFilthDetector],
                output_dict=True,
            ),
           {
               'macro avg': {'f1-score': 0.6666666666666666, 'precision': 1.0,'recall': 0.5, 'support': 4},
               'micro avg': {'f1-score': 0.6666666666666666, 'precision': 1.0, 'recall': 0.5, 'support': 4},
               'phone': {'f1-score': 0.6666666666666666, 'precision': 1.0, 'recall': 0.5, 'support': 4},
               'weighted avg': {'f1-score': 0.6666666666666666, 'precision': 1.0, 'recall': 0.5, 'support': 4}
           },
        )

    def test_false_positive(self):
        """test with incorrect identification"""
        filths = [
            PhoneFilth(beg=0, end=4, text='1234'),
            KnownFilth(beg=5, end=10, text='12345', comparison_type='phone'),
            MergedFilth(
                PhoneFilth(beg=5, end=9, text='1234'),
                KnownFilth(beg=5, end=9, text='1234', comparison_type='phone'),
            ),
            KnownFilth(beg=15, end=20, text='12345', comparison_type='phone'),
        ]

        self.assertEquals(
            scrubadub.comparison.compare_detectors_to_known_types(
                filths,
                [PhoneDetector, KnownFilthDetector],
                output_dict=True,
            ),
            {
                'phone': {'precision': 0.5, 'recall': 0.3333333333333333, 'f1-score': 0.4, 'support': 3},
                'micro avg': {'precision': 0.5, 'recall': 0.3333333333333333, 'f1-score': 0.4, 'support': 3},
                'macro avg': {'precision': 0.5, 'recall': 0.3333333333333333, 'f1-score': 0.4, 'support': 3},
                'weighted avg': {'precision': 0.5, 'recall': 0.3333333333333333, 'f1-score': 0.4000000000000001, 'support': 3}
            },
        )

    def test_two_comparisons(self):
        """test two filths in comparison"""

        class TempFilth(Filth):
            type = 'temp'

        class TempDetector(Detector):
            filth_cls = TempFilth

        filths = [
            MergedFilth(
                PhoneFilth(beg=0, end=4, text='1234'),
                KnownFilth(beg=0, end=4, text='1234', comparison_type='phone'),
            ),
            KnownFilth(beg=5, end=10, text='12345', comparison_type='phone'),
            MergedFilth(
                TempFilth(beg=5, end=9, text='1234'),
                KnownFilth(beg=5, end=9, text='1234', comparison_type='temp'),
            ),
            KnownFilth(beg=15, end=20, text='12345', comparison_type='temp'),
        ]

        self.assertEquals(
            scrubadub.comparison.compare_detectors_to_known_types(
                filths,
                [PhoneDetector, TempDetector, KnownFilthDetector],
                output_dict=True,
            ),
            {
                'phone': {'precision': 1.0, 'recall': 0.5, 'f1-score': 0.6666666666666666, 'support': 2},
                'temp': {'precision': 1.0, 'recall': 0.5, 'f1-score': 0.6666666666666666, 'support': 2},
                'micro avg': {'precision': 1.0, 'recall': 0.5, 'f1-score': 0.6666666666666666, 'support': 4},
                'macro avg': {'precision': 1.0, 'recall': 0.5, 'f1-score': 0.6666666666666666, 'support': 4},
                'weighted avg': {'precision': 1.0, 'recall': 0.5, 'f1-score': 0.6666666666666666, 'support': 4},
                'samples avg': {'precision': 0.5, 'recall': 0.5, 'f1-score': 0.5, 'support': 4}
            },
        )

    def test_other_predefined_types(self):
        """test comparison with other predefined filth types"""
        filths = [
            MergedFilth(
                PhoneFilth(beg=0, end=4, text='John'),
                KnownFilth(beg=0, end=4, text='John', comparison_type='phone')
            ),
            KnownFilth(beg=5, end=10, text='Hello', comparison_type='word'),
        ]

        self.assertEquals(
            scrubadub.comparison.compare_detectors_to_known_types(
                filths,
                [PhoneDetector, KnownFilthDetector],
                output_dict=True,
            ),
            {
                'phone': {'precision': 1.0, 'recall': 1.0, 'f1-score': 1.0, 'support': 1},
                'accuracy': 1.0, 'macro avg': {'precision': 1.0, 'recall': 1.0, 'f1-score': 1.0, 'support': 1},
                'weighted avg': {'precision': 1.0, 'recall': 1.0, 'f1-score': 1.0, 'support': 1}
            },
        )

    def test_with_irrelevant_filth(self):
        """text comparison with irrelevant filths included"""

        class TempFilth(Filth):
            type = 'temp'

        filths = [
            MergedFilth(
                PhoneFilth(beg=0, end=4, text='John'),
                KnownFilth(beg=0, end=4, text='John', comparison_type='phone')
            ),
            KnownFilth(beg=5, end=10, text='Hello', comparison_type='name'),
            KnownFilth(beg=5, end=10, text='Hello', comparison_type='temp'),
            TempFilth(beg=100, end=103, text='123'),
        ]

        self.assertEquals(
            scrubadub.comparison.compare_detectors_to_known_types(
                filths,
                [PhoneDetector, KnownFilthDetector],
                output_dict=True,
            ),
            {
                'phone': {'precision': 1.0, 'recall': 1.0, 'f1-score': 1.0, 'support': 1}, 'accuracy': 1.0,
                'macro avg': {'precision': 1.0, 'recall': 1.0, 'f1-score': 1.0, 'support': 1},
                'weighted avg': {'precision': 1.0, 'recall': 1.0, 'f1-score': 1.0, 'support': 1}
            },
        )
