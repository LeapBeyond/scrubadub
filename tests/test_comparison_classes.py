import unittest

from scrubadub.comparison import TextPosition, FilthTypePositions, FilthGrouper
from scrubadub.filth.base import MergedFilth
from scrubadub.filth.phone import PhoneFilth
from scrubadub.filth.tagged import TaggedEvaluationFilth

class ComparisonTestCase(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None

    def test_text_position(self):
        filth = PhoneFilth(beg=0, end=4, text='1234', detector_name='phone', locale='en_GB', document_name='test.txt')
        tp = TextPosition(filth, FilthGrouper.grouping_default)

        self.assertEqual(filth.beg, tp.beg)
        self.assertEqual(filth.end, tp.end)
        self.assertEqual(
            {('phone', 'phone', 'en_GB')},
            tp.detected,
        )
        self.assertEqual(set(), tp.tagged)
        self.assertEqual(filth.document_name, tp.document_name)

    def test_text_equality(self):
        filth = PhoneFilth(beg=0, end=4, text='1234', detector_name='phone', locale='en_GB', document_name='test.txt')
        tp = TextPosition(filth, FilthGrouper.grouping_default)
        tp2 = TextPosition(filth, FilthGrouper.grouping_default)
        self.assertTrue(tp == tp2)

        filth = PhoneFilth(beg=0, end=4, text='1234', detector_name='phone', locale='fr_FR', document_name='test.txt')
        tp2 = TextPosition(filth, FilthGrouper.grouping_default)
        self.assertTrue(tp != tp2)

        filth = PhoneFilth(beg=0, end=4, text='1234', detector_name='phone2', locale='en_GB', document_name='test.txt')
        tp2 = TextPosition(filth, FilthGrouper.grouping_default)
        self.assertTrue(tp != tp2)

        filth = PhoneFilth(beg=0, end=5, text='12345', detector_name='phone', locale='en_GB', document_name='test.txt')
        tp2 = TextPosition(filth, FilthGrouper.grouping_default)
        self.assertTrue(tp != tp2)

        filth = PhoneFilth(beg=0, end=4, text='1234', detector_name='phone', locale='en_GB', document_name='test2.txt')
        tp2 = TextPosition(filth, FilthGrouper.grouping_default)
        self.assertTrue(tp != tp2)

    def test_text_position_function(self):
        filth = PhoneFilth(beg=0, end=4, text='1234', detector_name='phone', locale='en_GB', document_name='test.txt')
        tp = TextPosition(filth, lambda x: {1:1, 2:2, 3:3})

        self.assertEqual(
            {(1, 2, 3)},
            tp.detected,
        )

    def test_text_position_merge(self):
        filth_a = PhoneFilth(
            beg=0, end=4, text='1234', detector_name='phone_a', locale='en_GB', document_name='test.txt'
        )
        filth_b = PhoneFilth(
            beg=3, end=6, text='1234', detector_name='phone_b', locale='en_GB', document_name='test.txt'
        )

        tp_a = TextPosition(filth_a, FilthGrouper.grouping_default)
        tp_b = TextPosition(filth_b, FilthGrouper.grouping_default)
        tp_a.merge(tp_b)

        self.assertEqual(0, tp_a.beg)
        self.assertEqual(6, tp_a.end)

        self.assertEqual(
            {
                ('phone', 'phone_a', 'en_GB'),
                ('phone', 'phone_b', 'en_GB'),
            },
            tp_a.detected,
        )
        self.assertEqual(set(), tp_a.tagged)

    def test_text_position_merge_files(self):
        filth_a = PhoneFilth(
            beg=0, end=4, text='1234', detector_name='phone_a', locale='en_GB', document_name='test1.txt'
        )
        filth_b = PhoneFilth(
            beg=3, end=6, text='1234', detector_name='phone_b', locale='en_GB', document_name='test2.txt'
        )

        tp_a = TextPosition(filth_a, FilthGrouper.grouping_default)
        tp_b = TextPosition(filth_b, FilthGrouper.grouping_default)

        with self.assertRaises(ValueError):
            tp_a.merge(tp_b)

    def test_text_position_merge_ranges(self):
        filth_a = PhoneFilth(
            beg=0, end=4, text='1234', detector_name='phone_a', locale='en_GB', document_name='test.txt'
        )
        filth_b = PhoneFilth(
            beg=10, end=14, text='1234', detector_name='phone_b', locale='en_GB', document_name='test.txt'
        )

        tp_a = TextPosition(filth_a, FilthGrouper.grouping_default)
        tp_b = TextPosition(filth_b, FilthGrouper.grouping_default)

        with self.assertRaises(ValueError):
            tp_a.merge(tp_b)

    def test_text_position_repr(self):
        filth = PhoneFilth(beg=0, end=4, text='1234', detector_name='phone_a', locale='en_GB', document_name='test.txt')
        tp = TextPosition(filth, FilthGrouper.grouping_default)
        self.assertEqual(
            "<TextPosition beg=0 end=4 tagged=set() detected={('phone', 'phone_a', 'en_GB')} document_name='test.txt'>",
            tp.__repr__()
        )

    def test_filth_type(self):
        filth_a = PhoneFilth(
            beg=0, end=4, text='1234', detector_name='phone_a', locale='en_GB', document_name='test.txt'
        )
        filth_b = PhoneFilth(
            beg=2, end=6, text='1234', detector_name='phone_b', locale='en_GB', document_name='test.txt'
        )
        filth_c = PhoneFilth(
            beg=10, end=14, text='1234', detector_name='phone_b', locale='en_GB', document_name='test.txt'
        )

        ft = FilthTypePositions(grouping_function=FilthGrouper.grouping_default, filth_type='phone')
        ft.add_filth(filth_c)
        ft.add_filth(filth_a)
        ft.add_filth(filth_b)
        self.assertEqual(3, len(ft.positions))
        self.assertEqual(10, ft.positions[0].beg)
        self.assertEqual(0, ft.positions[1].beg)
        self.assertEqual(2, ft.positions[2].beg)
        self.assertEqual(['filth', 'detector', 'locale'], ft.column_names)

        ft.merge_positions()
        self.assertEqual(2, len(ft.positions))
        self.assertEqual(10, ft.positions[1].beg)
        self.assertEqual(0, ft.positions[0].beg)
        self.assertEqual(6, ft.positions[0].end)
        self.assertEqual(
            {
                ('phone', 'phone_a', 'en_GB'),
                ('phone', 'phone_b', 'en_GB'),
            },
            ft.positions[0].detected,
        )

        df = ft.get_counts()
        self.assertEqual(['filth', 'detector', 'locale'], df.columns.names)
        self.assertEqual(
            {
                ('phone', 'phone_b', 'en_GB'),
                ('phone', 'phone_a', 'en_GB'),
            },
            set(df.columns.values.tolist()),
        )
        self.assertEqual([1, 0], df[('phone', 'phone_a', 'en_GB')].values.tolist())
        self.assertEqual([1, 1], df[('phone', 'phone_b', 'en_GB')].values.tolist())

    def test_filth_type_equality(self):
        filth_a = PhoneFilth(
            beg=0, end=4, text='1234', detector_name='phone_a', locale='en_GB', document_name='test.txt'
        )
        filth_b = PhoneFilth(
            beg=2, end=6, text='1234', detector_name='phone_b', locale='en_GB', document_name='test.txt'
        )
        filth_c = PhoneFilth(
            beg=10, end=14, text='1234', detector_name='phone_b', locale='en_GB', document_name='test.txt'
        )

        ft = FilthTypePositions(grouping_function=FilthGrouper.grouping_default, filth_type='phone')
        ft.add_filth(filth_c)
        ft.add_filth(filth_a)
        ft.add_filth(filth_b)

        ft2 = FilthTypePositions(grouping_function=FilthGrouper.grouping_default, filth_type='phone')
        ft2.add_filth(filth_c)
        ft2.add_filth(filth_a)
        ft2.add_filth(filth_b)

        self.assertTrue(ft == ft2)

        ft2 = FilthTypePositions(grouping_function=FilthGrouper.grouping_default, filth_type='phone')
        ft2.add_filth(filth_c)
        ft2.add_filth(filth_a)

        self.assertTrue(ft != ft2)

    def test_filth_type_touching(self):
        filth_a = PhoneFilth(
            beg=0, end=4, text='1234', detector_name='phone_a', locale='en_GB', document_name='test.txt'
        )
        filth_b = PhoneFilth(
            beg=2, end=6, text='1234', detector_name='phone_b', locale='en_GB', document_name='test.txt'
        )
        filth_c = PhoneFilth(
            beg=6, end=10, text='1234', detector_name='phone_b', locale='en_GB', document_name='test.txt'
        )

        ft = FilthTypePositions(grouping_function=FilthGrouper.grouping_default, filth_type='phone')
        ft.add_filth(filth_c)
        ft.add_filth(filth_a)
        ft.add_filth(filth_b)
        ft.merge_positions()

        self.assertEqual(2, len(ft.positions))


    def test_filth_grouper(self):
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
            TaggedEvaluationFilth(beg=30, end=35, text='12345', comparison_type='name', locale='en_US'),
        ]
        fg = FilthGrouper(combine_detectors=True, groupby_documents=False, filth_types=None)
        self.assertEqual(fg.grouping_function, FilthGrouper.grouping_combined)
        fg = FilthGrouper(combine_detectors=False, groupby_documents=False, filth_types=None)
        self.assertEqual(fg.grouping_function, FilthGrouper.grouping_default)

        fg.add_filths(filths)
        print(fg)
        self.assertEqual(['phone', 'name'], list(fg.types.keys()))
        self.assertEqual(1, len(fg.types['name'].positions))
        self.assertEqual(6, len(fg.types['phone'].positions))

        fg.merge_positions()
        self.assertEqual(1, len(fg.types['name'].positions))
        self.assertEqual(4, len(fg.types['phone'].positions))

        fg_from_list = FilthGrouper.from_filth_list(filths)
        self.assertEqual(list(fg.types.keys()), list(fg_from_list.types.keys()))

        df = fg.get_counts()
        print(df)
        self.assertEqual(['filth', 'detector', 'locale'], df.columns.names)
        self.assertEqual(
            [
                ('name', 'tagged', 'en_US'),
                ('phone', 'phone', 'en_GB'),
                ('phone', 'phone', 'en_US'),
                ('phone', 'tagged', 'en_GB'),
                ('phone', 'tagged', 'en_US')
            ],
            df.columns.values.tolist(),
        )
        self.assertEqual([0, 0, 0, 0, 1], df[('name', 'tagged', 'en_US')].values.tolist())
        self.assertEqual([1, 0, 0, 0, 0], df[('phone', 'phone', 'en_GB')].values.tolist())
        self.assertEqual([0, 0, 1, 0, 0], df[('phone', 'phone', 'en_US')].values.tolist())
        self.assertEqual([1, 1, 0, 0, 0], df[('phone', 'tagged', 'en_GB')].values.tolist())
        self.assertEqual([0, 0, 1, 1, 0], df[('phone', 'tagged', 'en_US')].values.tolist())

    def test_filth_grouper_equality(self):
        filths = [
            MergedFilth(
                PhoneFilth(beg=0, end=4, text='1234', detector_name='phone', locale='en_GB', document_name='gb.txt'),
                TaggedEvaluationFilth(beg=0, end=4, text='1234', comparison_type='phone', locale='en_GB',
                                      document_name='gb.txt'),
            ),
            TaggedEvaluationFilth(beg=5, end=10, text='12345', comparison_type='phone', locale='en_GB',
                                  document_name='gb.txt'),
            MergedFilth(
                PhoneFilth(beg=12, end=16, text='1234', detector_name='phone', locale='en_US', document_name='us.txt'),
                TaggedEvaluationFilth(beg=12, end=16, text='1234', comparison_type='phone', locale='en_US',
                                      document_name='us.txt'),
            ),
            TaggedEvaluationFilth(beg=20, end=25, text='12345', comparison_type='phone', locale='en_US',
                                  document_name='us.txt'),
            TaggedEvaluationFilth(beg=30, end=35, text='12345', comparison_type='name', locale='en_US',
                                  document_name='us.txt'),
        ]
        fg = FilthGrouper(combine_detectors=True, groupby_documents=True, filth_types=['phone'])
        fg.add_filths(filths)
        fg2 = FilthGrouper(combine_detectors=True, groupby_documents=True, filth_types=['phone'])
        fg2.add_filths(filths)

        self.assertTrue(fg == fg2)

        fg2 = FilthGrouper(combine_detectors=True, groupby_documents=True, filth_types=['phone'])
        fg2.add_filths(filths[1:])

        self.assertTrue(fg != fg2)

        fg2 = FilthGrouper(grouping_function=FilthGrouper.grouping_default, filth_types=['phone'])
        fg2.add_filths(filths[1:])

        self.assertTrue(fg != fg2)

        self.assertEqual(['phone'], list(fg.types.keys()))
        self.assertEqual(6, len(fg.types['phone'].positions))

        fg.merge_positions()
        self.assertEqual(4, len(fg.types['phone'].positions))

        fg_from_list = FilthGrouper.from_filth_list(filths, filth_types=['phone'], combine_detectors=True,
                                                    groupby_documents=True)
        self.assertEqual(list(fg.types.keys()), list(fg_from_list.types.keys()))

        df = fg.get_counts()
        self.assertEqual(['filth', 'document_name', 'detector', 'locale'], df.columns.names)
        self.assertEqual(
            [
                ('phone', 'gb.txt', 'combined', 'en_GB'),
                ('phone', 'gb.txt', 'tagged', 'en_GB'),
                ('phone', 'us.txt', 'combined', 'en_US'),
                ('phone', 'us.txt', 'tagged', 'en_US')
            ],
            df.columns.values.tolist(),
        )
        self.assertEqual([1, 0, 0, 0], df[('phone', 'gb.txt', 'combined', 'en_GB')].values.tolist())
        self.assertEqual([1, 1, 0, 0], df[('phone', 'gb.txt', 'tagged', 'en_GB')].values.tolist())
        self.assertEqual([0, 0, 1, 0], df[('phone', 'us.txt', 'combined', 'en_US')].values.tolist())
        self.assertEqual([0, 0, 1, 1], df[('phone', 'us.txt', 'tagged', 'en_US')].values.tolist())
