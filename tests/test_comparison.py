import unittest

import scrubadub
import scrubadub.comparison
from scrubadub.filth.base import MergedFilth, Filth
from scrubadub.filth.phone import PhoneFilth
from scrubadub.filth.known import KnownFilth
from scrubadub.detectors.base import Detector

class ComparisonTestCase(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None

    def test_comparison(self):
        """test basic comparison"""
        filths = [
            MergedFilth(
                PhoneFilth(beg=0, end=4, text='1234', detector_name='phone'),
                KnownFilth(beg=0, end=4, text='1234', comparison_type='phone'),
            ),
            KnownFilth(beg=5, end=10, text='12345', comparison_type='phone'),
            MergedFilth(
                PhoneFilth(beg=5, end=9, text='1234', detector_name='phone'),
                KnownFilth(beg=5, end=9, text='1234', comparison_type='phone'),
            ),
            KnownFilth(beg=15, end=20, text='12345', comparison_type='phone'),
        ]

        self.assertEquals(
            scrubadub.comparison.get_filth_classification_report(
                filths,
                output_dict=True,
            ),
            {
                'macro avg': {'f1-score': 0.6666666666666666, 'precision': 1.0,'recall': 0.5, 'support': 4},
                'micro avg': {'f1-score': 0.6666666666666666, 'precision': 1.0, 'recall': 0.5, 'support': 4},
                'phone:phone:None': {'f1-score': 0.6666666666666666, 'precision': 1.0, 'recall': 0.5, 'support': 4},
                'weighted avg': {'f1-score': 0.6666666666666666, 'precision': 1.0, 'recall': 0.5, 'support': 4}
            },
        )

    def test_text_output(self):
        """test basic comparison"""
        filths = [
            MergedFilth(
                PhoneFilth(beg=0, end=4, text='1234', detector_name='phone'),
                KnownFilth(beg=0, end=4, text='1234', comparison_type='phone'),
            ),
            KnownFilth(beg=5, end=10, text='12345', comparison_type='phone'),
            MergedFilth(
                PhoneFilth(beg=5, end=9, text='1234', detector_name='phone'),
                KnownFilth(beg=5, end=9, text='1234', comparison_type='phone'),
            ),
            KnownFilth(beg=15, end=20, text='12345', comparison_type='phone'),
        ]
        text = scrubadub.comparison.get_filth_classification_report(
            filths,
            output_dict=False,
        ).strip()
        print(text)
        self.assertEquals(
            text,
            "filth     detector     locale    precision    recall  f1-score   support\n"
            "\n"
            "phone        phone       None         1.00      0.50      0.67         4\n"
            "\n"
            "                      micro avg       1.00      0.50      0.67         4\n"
            "                      macro avg       1.00      0.50      0.67         4\n"
            "                   weighted avg       1.00      0.50      0.67         4\n".strip(),
        )

    def test_false_positive(self):
        """test with incorrect identification"""
        filths = [
            PhoneFilth(beg=0, end=4, text='1234', detector_name='phone_v1'),
            KnownFilth(beg=5, end=10, text='12345', comparison_type='phone'),
            MergedFilth(
                PhoneFilth(beg=5, end=9, text='1234', detector_name='phone_v1'),
                KnownFilth(beg=5, end=9, text='1234', comparison_type='phone'),
            ),
            KnownFilth(beg=15, end=20, text='12345', comparison_type='phone'),
        ]

        self.assertEquals(
            scrubadub.comparison.get_filth_classification_report(
                filths,
                # [PhoneDetector, KnownFilthDetector],
                output_dict=True,
            ),
            {
                'phone:phone_v1:None': {'precision': 0.5, 'recall': 0.3333333333333333, 'f1-score': 0.4, 'support': 3},
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
                PhoneFilth(beg=0, end=4, text='1234', detector_name='phone'),
                KnownFilth(beg=0, end=4, text='1234', comparison_type='phone'),
            ),
            KnownFilth(beg=5, end=10, text='12345', comparison_type='phone'),
            MergedFilth(
                TempFilth(beg=5, end=9, text='1234', detector_name='temp'),
                KnownFilth(beg=5, end=9, text='1234', comparison_type='temp'),
            ),
            KnownFilth(beg=15, end=20, text='12345', comparison_type='temp'),
        ]

        self.assertEquals(
            scrubadub.comparison.get_filth_classification_report(
                filths,
                output_dict=True,
            ),
            {
                'phone:phone:None': {'precision': 1.0, 'recall': 0.5, 'f1-score': 0.6666666666666666, 'support': 2},
                'temp:temp:None': {'precision': 1.0, 'recall': 0.5, 'f1-score': 0.6666666666666666, 'support': 2},
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
                PhoneFilth(beg=0, end=4, text='John', detector_name='phone'),
                KnownFilth(beg=0, end=4, text='John', comparison_type='phone')
            ),
            KnownFilth(beg=5, end=10, text='Hello', comparison_type='word'),
        ]

        self.assertEquals(
            scrubadub.comparison.get_filth_classification_report(
                filths,
                # [PhoneDetector, KnownFilthDetector],
                output_dict=True,
            ),
            {
                'phone:phone:None': {'precision': 1.0, 'recall': 1.0, 'f1-score': 1.0, 'support': 1},
                'micro avg': {'precision': 1.0, 'recall': 1.0, 'f1-score': 1.0, 'support': 1},
                'macro avg': {'precision': 1.0, 'recall': 1.0, 'f1-score': 1.0, 'support': 1},
                'weighted avg': {'precision': 1.0, 'recall': 1.0, 'f1-score': 1.0, 'support': 1}
            },

        )

    def test_locales(self):
        """test comparison with other predefined filth types"""

        filths = [
            MergedFilth(
                PhoneFilth(beg=0, end=4, text='1234', detector_name='phone', locale='en_GB'),
                KnownFilth(beg=0, end=4, text='1234', comparison_type='phone', locale='en_GB'),
            ),
            KnownFilth(beg=5, end=10, text='12345', comparison_type='phone', locale='en_GB'),
            MergedFilth(
                PhoneFilth(beg=5, end=9, text='1234', detector_name='phone', locale='en_US'),
                KnownFilth(beg=5, end=9, text='1234', comparison_type='phone', locale='en_US'),
            ),
            KnownFilth(beg=15, end=20, text='12345', comparison_type='phone', locale='en_US'),
        ]

        self.assertEquals(
            scrubadub.comparison.get_filth_classification_report(
                filths,
                output_dict=True,
            ),
            {
                'macro avg': {'f1-score': 0.6666666666666666, 'precision': 1.0,'recall': 0.5, 'support': 4},
                'micro avg': {'f1-score': 0.6666666666666666, 'precision': 1.0, 'recall': 0.5, 'support': 4},
                'phone:phone:en_GB': {'f1-score': 0.6666666666666666, 'precision': 1.0, 'recall': 0.5, 'support': 2},
                'phone:phone:en_US': {'f1-score': 0.6666666666666666, 'precision': 1.0, 'recall': 0.5, 'support': 2},
                'samples avg': {'f1-score': 0.5, 'precision': 0.5, 'recall': 0.5, 'support': 4},
                'weighted avg': {'f1-score': 0.6666666666666666, 'precision': 1.0, 'recall': 0.5, 'support': 4}
            },
        )

    def test_with_irrelevant_filth(self):
        """text comparison with irrelevant filths included"""

        class TempFilth(Filth):
            type = 'temp'

        filths = [
            MergedFilth(
                PhoneFilth(beg=0, end=4, text='John', detector_name='phone'),
                KnownFilth(beg=0, end=4, text='John', comparison_type='phone')
            ),
            KnownFilth(beg=5, end=10, text='Hello', comparison_type='name'),
            # KnownFilth(beg=5, end=10, text='Hello', comparison_type='temp'),
            TempFilth(beg=100, end=103, text='123', detector_name='temp'),
        ]

        self.assertEquals(
            scrubadub.comparison.get_filth_classification_report(
                filths,
                # [PhoneDetector, KnownFilthDetector],
                output_dict=True,
            ),
            {
                'phone:phone:None': {'precision': 1.0, 'recall': 1.0, 'f1-score': 1.0, 'support': 1},
                'micro avg': {'precision': 1.0, 'recall': 1.0, 'f1-score': 1.0, 'support': 1},
                'macro avg': {'precision': 1.0, 'recall': 1.0, 'f1-score': 1.0, 'support': 1},
                'weighted avg': {'precision': 1.0, 'recall': 1.0, 'f1-score': 1.0, 'support': 1}
            },
        )

    def test_empty(self):
        """Test return value of empty list of filth"""

        self.assertTrue(
            scrubadub.comparison.get_filth_classification_report(
                [],
                output_dict=True,
            ) is None,
        )

    def test_dataframe(self):
        """test basic comparison"""
        filths = [
            MergedFilth(
                PhoneFilth(beg=0, end=4, text='1234', detector_name='phone'),
                KnownFilth(beg=0, end=4, text='1234', comparison_type='phone'),
            ),
            KnownFilth(beg=5, end=10, text='12345', comparison_type='phone'),
            MergedFilth(
                PhoneFilth(beg=4, end=9, text=' 1234', detector_name='phone'),
                KnownFilth(beg=5, end=9, text='1234', comparison_type='phone'),
            ),
            KnownFilth(beg=15, end=20, text='12345', comparison_type='phone'),
        ]
        dataframe = scrubadub.comparison.get_filth_dataframe(
            filths,
        )
        self.assertEquals(dataframe.shape[0], 4)
        self.assertEquals(dataframe['filth_type'].fillna('none').values.tolist(), ['phone', 'phone', 'none', 'none'])
        self.assertEquals(dataframe['beg'].fillna('none').values.tolist(), [0, 4, 'none', 'none'])
        self.assertEquals(dataframe['end'].fillna('none').values.tolist(), [4, 9, 'none', 'none'])
        self.assertEquals(dataframe['known_beg'].fillna('none').values.tolist(), [0, 5, 5, 15])
        self.assertEquals(dataframe['known_end'].fillna('none').values.tolist(), [4, 9, 10, 20])
        self.assertEquals(dataframe['exact_match'].fillna('none').values.tolist(), [True, False, False, False])
        self.assertEquals(dataframe['partial_match'].fillna('none').values.tolist(), [True, True, False, False])
        self.assertEquals(dataframe['true_positive'].fillna('none').values.tolist(), [True, True, False, False])
        self.assertEquals(dataframe['false_positive'].fillna('none').values.tolist(), [False, False, False, False])
        self.assertEquals(dataframe['false_negative'].fillna('none').values.tolist(), [False, False, True, True])

    def test_make_document(self):
        document, known_filths = scrubadub.comparison.make_fake_document(paragraphs=1, seed=0)
        total_len = 0
        for filth_item in known_filths:
            self.assertIn(filth_item['match'], document)
            total_len += len(filth_item['match'])
        self.assertTrue(len(document) > 2 * total_len)

        document, known_filths = scrubadub.comparison.make_fake_document(paragraphs=1, seed=0, filth_types=['email'])
        total_len = 0
        for filth_item in known_filths:
            self.assertIn(filth_item['match'], document)
            total_len += len(filth_item['match'])
            self.assertEquals(filth_item['filth_type'], 'email')
        self.assertTrue(len(document) > 2 * total_len)
