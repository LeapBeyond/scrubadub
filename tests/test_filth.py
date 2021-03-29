import re
import unittest

from scrubadub.filth import Filth, MergedFilth
from scrubadub.exceptions import InvalidReplaceWith, FilthMergeError

class FilthTestCase(unittest.TestCase):

    def test_disallowed_replace_with(self):
        """replace_with should fail gracefully"""
        filth = Filth(beg=0, end=3, text='asd')
        with self.assertRaises(InvalidReplaceWith):
            filth.replace_with('surrogate')
        with self.assertRaises(InvalidReplaceWith):
            filth.replace_with('something_invalid')

    def test_nonoverlapping_filth(self):
        """can't merge non-overlapping filth"""
        a_filth = Filth(beg=0, end=3, text="the")
        b_filth = Filth(beg=4, end=7, text="end")
        with self.assertRaises(FilthMergeError):
            a_filth.merge(b_filth)
        with self.assertRaises(FilthMergeError):
            b_filth.merge(a_filth)

    def test_text_merge(self):
        """make sure text length is correct"""
        class SomeFilth(Filth):
            type = 'something'

        text = "the end"
        a_filth = SomeFilth(beg=0, end=3, text=text[:3])
        b_filth = SomeFilth(beg=1, end=7, text=text[1:])

        c_filth = a_filth.merge(b_filth)
        self.assertEqual(c_filth.text, text)

        c_filth = b_filth.merge(a_filth)
        self.assertEqual(c_filth.text, text)

        d_filth = c_filth.merge(a_filth)
        self.assertEqual(d_filth.text, text)

        b_filth.end = 2
        with self.assertRaises(FilthMergeError):
            b_filth.merge(a_filth)

    def test_invalid_merge_documents(self):
        """Ensure Filth in two different documents cant be merged"""
        filth_a = Filth(0, 2, text='aa', document_name='one')
        filth_b = Filth(1, 2, text='a', document_name='two')

        with self.assertRaises(FilthMergeError):
            filth_a.merge(filth_b)

        with self.assertRaises(FilthMergeError):
            filth_b.merge(filth_a)

    def test_filth_string(self):
        """Test the Filth to string function"""

        filth = Filth(beg=0, end=5)
        self.assertEqual(str(filth), "<Filth text='' beg=0 end=5>")

        filth = Filth(beg=0, end=5)
        self.assertEqual(filth.__repr__(), "<Filth text='' beg=0 end=5>")

        filth = Filth(beg=0, end=5)
        self.assertEqual(filth._to_string(), "<Filth text='' beg=0 end=5>")

        filth = Filth(beg=0, end=5, text='hello')
        self.assertEqual(str(filth), "<Filth text='hello' beg=0 end=5>")

        filth = Filth(beg=0, end=5, text='hello', document_name='hello.txt')
        self.assertEqual(str(filth), "<Filth text='hello' document_name='hello.txt' beg=0 end=5>")

        filth = Filth(beg=0, end=5, text='hello', document_name='hello.txt')
        self.assertEqual(filth._to_string(attributes=['text']), "<Filth text='hello'>")
        self.assertEqual(filth._to_string(attributes=['beg', 'end', 'text']), "<Filth beg=0 end=5 text='hello'>")
        self.assertEqual(
            filth._to_string(attributes=['text', 'document_name']),
            "<Filth text='hello' document_name='hello.txt'>"
        )

    def test_merged_to_string(self):
        """Test the MergedFilth to string"""
        class TestFilth(Filth):
            type = 'test_filth'

        merged = MergedFilth(TestFilth(0, 2, 'ab'), Filth(1, 2, 'b'))
        self.assertEqual(merged.__repr__(), "<MergedFilth filths=[<TestFilth text='ab' beg=0 end=2>, <Filth text='b' beg=1 end=2>]>")

    def test_equality(self):
        """Test the filth equality function"""
        self.assertTrue(
            Filth(beg=0, end=5, text='hello') ==
            Filth(beg=0, end=5, text='hello')
        )
        self.assertTrue(
            Filth(beg=0, end=5, text='hello') ==
            Filth(beg=0, end=5, text='hello', match=re.match('123', '1234'))
        )

        self.assertTrue(
            Filth(beg=0, end=5, text='hello') !=
            Filth(beg=1, end=5, text='hello')
        )
        self.assertTrue(
            Filth(beg=0, end=5, text='hello') !=
            Filth(beg=0, end=6, text='hello')
        )
        self.assertTrue(
            Filth(beg=0, end=5, text='hello') !=
            Filth(beg=0, end=5, text='hellou')
        )

        self.assertTrue(
            Filth(beg=0, end=5, text='hello', document_name='test') ==
            Filth(beg=0, end=5, text='hello', document_name='test')
        )
        self.assertTrue(
            Filth(beg=0, end=5, text='hello') !=
            Filth(beg=0, end=5, text='hello', document_name='test')
        )
        self.assertTrue(
            Filth(beg=0, end=5, text='hello', document_name='test') !=
            Filth(beg=0, end=5, text='hello')
        )
        self.assertTrue(
            Filth(beg=0, end=5, text='hello', document_name='test') !=
            Filth(beg=0, end=5, text='hello', document_name='another_test')
        )

        self.assertTrue(
            Filth(beg=0, end=5, text='hello', detector_name='tester') ==
            Filth(beg=0, end=5, text='hello', detector_name='tester')
        )
        self.assertTrue(
            Filth(beg=0, end=5, text='hello', detector_name='tester') !=
            Filth(beg=0, end=5, text='hello', detector_name='another_tester')
        )
        self.assertTrue(
            Filth(beg=0, end=5, text='hello', detector_name='tester') !=
            Filth(beg=0, end=5, text='hello')
        )
        self.assertTrue(
            Filth(beg=0, end=5, text='hello') !=
            Filth(beg=0, end=5, text='hello', detector_name='tester')
        )

        self.assertTrue(
            Filth(beg=0, end=5, text='hello', document_name='test', detector_name='tester') ==
            Filth(beg=0, end=5, text='hello', document_name='test', detector_name='tester')
        )
        self.assertTrue(
            Filth(beg=0, end=5, text='hello', document_name='test', detector_name='tester') !=
            Filth(beg=0, end=5, text='hello', document_name='test', detector_name='another_tester')
        )
        self.assertTrue(
            Filth(beg=0, end=5, text='hello', document_name='test', detector_name='tester') !=
            Filth(beg=0, end=5, text='hello', document_name='another_test', detector_name='tester')
        )