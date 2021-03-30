import unittest

import scrubadub
import scrubadub.comparison
from scrubadub.filth.base import MergedFilth, Filth
from scrubadub.filth.phone import PhoneFilth
from scrubadub.filth.address import AddressFilth
from scrubadub.filth.tagged import TaggedEvaluationFilth
from scrubadub.detectors.base import Detector

class ComparisonTestCase(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None


    def test_grouper(self):
        filths = [
            MergedFilth(
                PhoneFilth(beg=0, end=4, text='John', detector_name='phone_det'),
                TaggedEvaluationFilth(beg=0, end=4, text='John', comparison_type='phone')
            ),
            TaggedEvaluationFilth(beg=5, end=10, text='Hello', comparison_type='name'),
            AddressFilth(beg=100, end=103, text='123', detector_name='address_det'),
        ]
        grouper = scrubadub.comparison.FilthGrouper()
        grouper.add_filths(filths)

        self.assertEqual(3, len(grouper.types))

        self.assertEqual(2, len(grouper.types['phone'].positions))
        self.assertEqual(0, grouper.types['phone'].positions[0].beg)
        self.assertEqual(4, grouper.types['phone'].positions[0].end)
        self.assertEqual({('phone', 'phone_det', 'None')}, grouper.types['phone'].positions[0].detected)
        self.assertEqual(set(), grouper.types['phone'].positions[0].tagged)
        self.assertEqual(set(), grouper.types['phone'].positions[1].detected)
        self.assertEqual({('phone', 'tagged', 'None')}, grouper.types['phone'].positions[1].tagged)

        self.assertEqual(1, len(grouper.types['name'].positions))
        self.assertEqual(5, grouper.types['name'].positions[0].beg)
        self.assertEqual(10, grouper.types['name'].positions[0].end)
        self.assertEqual({('name', 'tagged', 'None')}, grouper.types['name'].positions[0].tagged)
        self.assertEqual(set(), grouper.types['name'].positions[0].detected)

        self.assertEqual(1, len(grouper.types['address'].positions))
        self.assertEqual(100, grouper.types['address'].positions[0].beg)
        self.assertEqual(103, grouper.types['address'].positions[0].end)
        self.assertEqual(set(), grouper.types['address'].positions[0].tagged)
        self.assertEqual({('address', 'address_det', 'None')}, grouper.types['address'].positions[0].detected)

        grouper.merge_positions()

        self.assertEqual(3, len(grouper.types))

        self.assertEqual(1, len(grouper.types['phone'].positions))
        self.assertEqual(0, grouper.types['phone'].positions[0].beg)
        self.assertEqual(4, grouper.types['phone'].positions[0].end)
        self.assertEqual({('phone', 'phone_det', 'None')}, grouper.types['phone'].positions[0].detected)
        self.assertEqual({('phone', 'tagged', 'None')}, grouper.types['phone'].positions[0].tagged)

        self.assertEqual(1, len(grouper.types['name'].positions))
        self.assertEqual(5, grouper.types['name'].positions[0].beg)
        self.assertEqual(10, grouper.types['name'].positions[0].end)
        self.assertEqual({('name', 'tagged', 'None')}, grouper.types['name'].positions[0].tagged)
        self.assertEqual(set(), grouper.types['name'].positions[0].detected)

        self.assertEqual(1, len(grouper.types['address'].positions))
        self.assertEqual(100, grouper.types['address'].positions[0].beg)
        self.assertEqual(103, grouper.types['address'].positions[0].end)
        self.assertEqual(set(), grouper.types['address'].positions[0].tagged)
        self.assertEqual({('address', 'address_det', 'None')}, grouper.types['address'].positions[0].detected)


    def test_comparison(self):
        """test basic comparison"""
        filths = [
            MergedFilth(
                PhoneFilth(beg=0, end=4, text='1234', detector_name='phone'),
                TaggedEvaluationFilth(beg=0, end=4, text='1234', comparison_type='phone'),
            ),
            TaggedEvaluationFilth(beg=5, end=10, text='12345', comparison_type='phone'),
            MergedFilth(
                PhoneFilth(beg=12, end=16, text='1234', detector_name='phone'),
                TaggedEvaluationFilth(beg=12, end=16, text='1234', comparison_type='phone'),
            ),
            TaggedEvaluationFilth(beg=20, end=25, text='12345', comparison_type='phone'),
        ]

        self.assertEqual(
            {
                'macro avg': {'f1-score': 0.6666666666666666, 'precision': 1.0,'recall': 0.5, 'support': 4},
                'micro avg': {'f1-score': 0.6666666666666666, 'precision': 1.0, 'recall': 0.5, 'support': 4},
                'phone:phone:None': {'f1-score': 0.6666666666666666, 'precision': 1.0, 'recall': 0.5, 'support': 4},
                'weighted avg': {'f1-score': 0.6666666666666666, 'precision': 1.0, 'recall': 0.5, 'support': 4}
            },
            scrubadub.comparison.get_filth_classification_report(
                filths,
                output_dict=True,
            ),
        )

    def test_text_output(self):
        """test basic comparison"""
        filths = [
            MergedFilth(
                PhoneFilth(beg=0, end=4, text='1234', detector_name='phone'),
                TaggedEvaluationFilth(beg=0, end=4, text='1234', comparison_type='phone'),
            ),
            TaggedEvaluationFilth(beg=5, end=10, text='12345', comparison_type='phone'),
            MergedFilth(
                PhoneFilth(beg=11, end=15, text='1234', detector_name='phone'),
                TaggedEvaluationFilth(beg=11, end=15, text='1234', comparison_type='phone'),
            ),
            TaggedEvaluationFilth(beg=16, end=21, text='12345', comparison_type='phone'),
        ]
        text = scrubadub.comparison.get_filth_classification_report(
            filths,
            output_dict=False,
        ).strip()
        self.assertEqual(
            "filth    detector    locale      precision    recall  f1-score   support\n"
            "\n"
            "phone    phone       None             1.00      0.50      0.67         4\n"
            "\n"
            "                      micro avg       1.00      0.50      0.67         4\n"
            "                      macro avg       1.00      0.50      0.67         4\n"
            "                   weighted avg       1.00      0.50      0.67         4\n".strip(),
            text,
        )

    def test_false_positive(self):
        """test with incorrect identification"""
        filths = [
            PhoneFilth(beg=0, end=4, text='1234', detector_name='phone_v1'),
            TaggedEvaluationFilth(beg=5, end=10, text='12345', comparison_type='phone'),
            MergedFilth(
                PhoneFilth(beg=12, end=16, text='1234', detector_name='phone_v1'),
                TaggedEvaluationFilth(beg=12, end=16, text='1234', comparison_type='phone'),
            ),
            TaggedEvaluationFilth(beg=20, end=25, text='12345', comparison_type='phone'),
        ]

        self.assertEqual(
            {
                'phone:phone_v1:None': {'precision': 0.5, 'recall': 0.3333333333333333, 'f1-score': 0.4, 'support': 3},
                'micro avg': {'precision': 0.5, 'recall': 0.3333333333333333, 'f1-score': 0.4, 'support': 3},
                'macro avg': {'precision': 0.5, 'recall': 0.3333333333333333, 'f1-score': 0.4, 'support': 3},
                'weighted avg': {'precision': 0.5, 'recall': 0.3333333333333333, 'f1-score': 0.4000000000000001, 'support': 3}
            },
            scrubadub.comparison.get_filth_classification_report(
                filths,
                # [PhoneDetector, KnownFilthDetector],
                output_dict=True,
            ),
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
                TaggedEvaluationFilth(beg=0, end=4, text='1234', comparison_type='phone'),
            ),
            TaggedEvaluationFilth(beg=5, end=10, text='12345', comparison_type='phone'),
            MergedFilth(
                TempFilth(beg=5, end=9, text='1234', detector_name='temp'),
                TaggedEvaluationFilth(beg=5, end=9, text='1234', comparison_type='temp'),
            ),
            TaggedEvaluationFilth(beg=15, end=20, text='12345', comparison_type='temp'),
        ]

        self.assertEqual(
            {
                'phone:phone:None': {'precision': 1.0, 'recall': 0.5, 'f1-score': 0.6666666666666666, 'support': 2},
                'temp:temp:None': {'precision': 1.0, 'recall': 0.5, 'f1-score': 0.6666666666666666, 'support': 2},
                'micro avg': {'precision': 1.0, 'recall': 0.5, 'f1-score': 0.6666666666666666, 'support': 4},
                'macro avg': {'precision': 1.0, 'recall': 0.5, 'f1-score': 0.6666666666666666, 'support': 4},
                'weighted avg': {'precision': 1.0, 'recall': 0.5, 'f1-score': 0.6666666666666666, 'support': 4},
                'samples avg': {'precision': 0.5, 'recall': 0.5, 'f1-score': 0.5, 'support': 4}
            },
            scrubadub.comparison.get_filth_classification_report(
                filths,
                output_dict=True,
            ),
        )

    def test_other_predefined_types(self):
        """test comparison with other predefined filth types"""
        filths = [
            MergedFilth(
                PhoneFilth(beg=0, end=4, text='John', detector_name='phone'),
                TaggedEvaluationFilth(beg=0, end=4, text='John', comparison_type='phone')
            ),
            TaggedEvaluationFilth(beg=5, end=10, text='Hello', comparison_type='word'),
        ]

        self.assertEqual(
            {
                'phone:phone:None': {'precision': 1.0, 'recall': 1.0, 'f1-score': 1.0, 'support': 1},
                'micro avg': {'precision': 1.0, 'recall': 1.0, 'f1-score': 1.0, 'support': 1},
                'macro avg': {'precision': 1.0, 'recall': 1.0, 'f1-score': 1.0, 'support': 1},
                'weighted avg': {'precision': 1.0, 'recall': 1.0, 'f1-score': 1.0, 'support': 1}
            },
            scrubadub.comparison.get_filth_classification_report(
                filths,
                # [PhoneDetector, KnownFilthDetector],
                output_dict=True,
            ),

        )

    def test_locales(self):
        """test comparison with other predefined filth types"""

        filths = [
            MergedFilth(
                PhoneFilth(beg=0, end=4, text='1234', detector_name='phone', locale='en_GB'),
                TaggedEvaluationFilth(beg=0, end=4, text='1234', comparison_type='phone', locale='en_GB'),
            ),
            TaggedEvaluationFilth(beg=5, end=10, text='12345', comparison_type='phone', locale='en_GB'),
            MergedFilth(
                PhoneFilth(beg=12, end=16, text='1234', detector_name='phone', locale='en_US'),
                TaggedEvaluationFilth(beg=12, end=16, text='1234', comparison_type='phone', locale='en_US'),
            ),
            TaggedEvaluationFilth(beg=20, end=25, text='12345', comparison_type='phone', locale='en_US'),
        ]

        self.assertEqual(
            {
                'macro avg': {'f1-score': 0.6666666666666666, 'precision': 1.0,'recall': 0.5, 'support': 4},
                'micro avg': {'f1-score': 0.6666666666666666, 'precision': 1.0, 'recall': 0.5, 'support': 4},
                'phone:phone:en_GB': {'f1-score': 0.6666666666666666, 'precision': 1.0, 'recall': 0.5, 'support': 2},
                'phone:phone:en_US': {'f1-score': 0.6666666666666666, 'precision': 1.0, 'recall': 0.5, 'support': 2},
                'samples avg': {'f1-score': 0.5, 'precision': 0.5, 'recall': 0.5, 'support': 4},
                'weighted avg': {'f1-score': 0.6666666666666666, 'precision': 1.0, 'recall': 0.5, 'support': 4}
            },
            scrubadub.comparison.get_filth_classification_report(
                filths,
                output_dict=True,
            ),
        )

    def test_overall(self):
        """test comparison with other predefined filth types"""

        filths = [
            MergedFilth(
                PhoneFilth(beg=0, end=4, text='1234', detector_name='phone1', locale='en_GB'),
                TaggedEvaluationFilth(beg=0, end=4, text='1234', comparison_type='phone', locale='en_GB'),
            ),
            TaggedEvaluationFilth(beg=5, end=10, text='12345', comparison_type='phone', locale='en_GB'),
            MergedFilth(
                PhoneFilth(beg=12, end=16, text='1234', detector_name='phone2', locale='en_US'),
                TaggedEvaluationFilth(beg=12, end=16, text='1234', comparison_type='phone', locale='en_US'),
            ),
            TaggedEvaluationFilth(beg=20, end=25, text='12345', comparison_type='phone', locale='en_US'),
        ]

        self.assertEqual(
            {
                'macro avg': {'f1-score': 0.6666666666666666, 'precision': 1.0,'recall': 0.5, 'support': 4},
                'micro avg': {'f1-score': 0.6666666666666666, 'precision': 1.0, 'recall': 0.5, 'support': 4},
                'phone:combined:en_GB': {'f1-score': 0.6666666666666666, 'precision': 1.0, 'recall': 0.5, 'support': 2},
                'phone:combined:en_US': {'f1-score': 0.6666666666666666, 'precision': 1.0, 'recall': 0.5, 'support': 2},
                'samples avg': {'f1-score': 0.5, 'precision': 0.5, 'recall': 0.5, 'support': 4},
                'weighted avg': {'f1-score': 0.6666666666666666, 'precision': 1.0, 'recall': 0.5, 'support': 4}
            },
            scrubadub.comparison.get_filth_classification_report(
                filths,
                combine_detectors=True,
                output_dict=True,
            ),
        )

    def test_with_irrelevant_filth(self):
        """text comparison with irrelevant filths included"""

        class TempFilth(Filth):
            type = 'temp'

        filths = [
            MergedFilth(
                PhoneFilth(beg=0, end=4, text='John', detector_name='phone'),
                TaggedEvaluationFilth(beg=0, end=4, text='John', comparison_type='phone')
            ),
            TaggedEvaluationFilth(beg=5, end=10, text='Hello', comparison_type='name'),
            # KnownFilth(beg=5, end=10, text='Hello', comparison_type='temp'),
            TempFilth(beg=100, end=103, text='123', detector_name='temp'),
        ]

        self.assertEqual(
            {
                'phone:phone:None': {'precision': 1.0, 'recall': 1.0, 'f1-score': 1.0, 'support': 1},
                'micro avg': {'precision': 1.0, 'recall': 1.0, 'f1-score': 1.0, 'support': 1},
                'macro avg': {'precision': 1.0, 'recall': 1.0, 'f1-score': 1.0, 'support': 1},
                'weighted avg': {'precision': 1.0, 'recall': 1.0, 'f1-score': 1.0, 'support': 1}
            },
            scrubadub.comparison.get_filth_classification_report(
                filths,
                # [PhoneDetector, KnownFilthDetector],
                output_dict=True,
            ),
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
        # test to ensure it doesn't crash if no filth is given to get_filth_dataframe
        scrubadub.comparison.get_filth_dataframe([])
        # setup some filths for the other tests
        filths = [
            MergedFilth(
                PhoneFilth(beg=0, end=4, text='1234', detector_name='phone'),
                TaggedEvaluationFilth(beg=0, end=4, text='1234', comparison_type='phone'),
            ),
            TaggedEvaluationFilth(beg=5, end=10, text='12345', comparison_type='phone'),
            MergedFilth(
                PhoneFilth(beg=4, end=9, text=' 1234', detector_name='phone'),
                TaggedEvaluationFilth(beg=5, end=9, text='1234', comparison_type='phone'),
            ),
            TaggedEvaluationFilth(beg=15, end=20, text='12345', comparison_type='phone'),
        ]
        dataframe = scrubadub.comparison.get_filth_dataframe(
            filths,
        )
        self.assertEqual(4, dataframe.shape[0])
        self.assertEqual(
            ['phone', 'phone', 'none', 'none'],
            dataframe['filth_type'].fillna('none').values.tolist(),
        )
        self.assertEqual(
            [0, 4, 'none', 'none'],
            dataframe['beg'].fillna('none').values.tolist(),
        )
        self.assertEqual(
            [4, 9, 'none', 'none'],
            dataframe['end'].fillna('none').values.tolist(),
        )
        self.assertEqual(
            [0, 5, 5, 15],
            dataframe['known_beg'].fillna('none').values.tolist(),
        )
        self.assertEqual(
            [4, 9, 10, 20],
            dataframe['known_end'].fillna('none').values.tolist(),
        )
        self.assertEqual(
            [True, False, False, False],
            dataframe['exact_match'].fillna('none').values.tolist(),
        )
        self.assertEqual(
            [True, True, False, False],
            dataframe['partial_match'].fillna('none').values.tolist(),
        )
        self.assertEqual(
            [True, True, False, False],
            dataframe['true_positive'].fillna('none').values.tolist(),
        )
        self.assertEqual(
            [False, False, False, False],
            dataframe['false_positive'].fillna('none').values.tolist(),
        )
        self.assertEqual(
            [False, False, True, True],
            dataframe['false_negative'].fillna('none').values.tolist(),
        )

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
            self.assertEqual(filth_item['filth_type'], 'email')
        self.assertTrue(len(document) > 2 * total_len)

    def test_groupby_document(self):
        """test grouping by documents"""
        filths = [
            PhoneFilth(beg=0, end=4, text='1234', detector_name='phone_v1', document_name='1.txt'),
            TaggedEvaluationFilth(beg=5, end=10, text='12345', comparison_type='phone', document_name='1.txt'),
            MergedFilth(
                PhoneFilth(beg=12, end=16, text='1234', detector_name='phone_v1', document_name='1.txt'),
                TaggedEvaluationFilth(beg=12, end=16, text='1234', comparison_type='phone', document_name='1.txt'),
            ),
            TaggedEvaluationFilth(beg=20, end=25, text='12345', comparison_type='phone', document_name='1.txt'),
            PhoneFilth(beg=0, end=4, text='1234', detector_name='phone_v1', document_name='2.txt'),
            TaggedEvaluationFilth(beg=5, end=10, text='12345', comparison_type='phone', document_name='2.txt'),
            MergedFilth(
                PhoneFilth(beg=12, end=16, text='1234', detector_name='phone_v1', document_name='2.txt'),
                TaggedEvaluationFilth(beg=12, end=16, text='1234', comparison_type='phone', document_name='2.txt'),
            ),
            TaggedEvaluationFilth(beg=20, end=25, text='12345', comparison_type='phone', document_name='2.txt'),
        ]

        self.assertEqual(
            {
                'phone:1.txt:phone_v1:None': {'precision': 0.5, 'recall': 0.3333333333333333, 'f1-score': 0.4, 'support': 3},
                'phone:2.txt:phone_v1:None': {'precision': 0.5, 'recall': 0.3333333333333333, 'f1-score': 0.4, 'support': 3},
                'micro avg': {'precision': 0.5, 'recall': 0.3333333333333333, 'f1-score': 0.4, 'support': 6},
                'macro avg': {'precision': 0.5, 'recall': 0.3333333333333333, 'f1-score': 0.4, 'support': 6},
                'samples avg': {'f1-score': 0.25, 'precision': 0.25, 'recall': 0.25, 'support': 6},
                'weighted avg': {'precision': 0.5, 'recall': 0.3333333333333333, 'f1-score': 0.4000000000000001, 'support': 6}
            },
            scrubadub.comparison.get_filth_classification_report(
                filths,
                output_dict=True,
                groupby_documents=True,
            ),
        )