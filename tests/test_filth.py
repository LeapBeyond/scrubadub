import unittest

from scrubadub.filth import Filth
from scrubadub.exceptions import InvalidReplaceWith, FilthMergeError

class FilthTestCase(unittest.TestCase):

    def test_disallowed_replace_with(self):
        """replace_with should fail gracefully"""
        filth = Filth()
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
