import unittest

from scrubadub.utils import LowerCaseSet

class LowerCaseSetTestCase(unittest.TestCase):

    def test_init(self):
        """make sure that lower case casting works in __init__"""
        s = LowerCaseSet(['TKTK', 'tKtK', 'Tktk'])
        self.assertTrue('tktk' in s)
        self.assertEqual(len(s), 1)

    def test_add(self):
        """make sure that lower case casting works in add"""
        s = LowerCaseSet()
        s.add('TKTK')
        s.add('tKtK')
        s.add('Tktk')
        self.assertTrue('tktk' in s)
        self.assertEqual(len(s), 1)

    def test_update(self):
        """make sure lower case casting works in update"""
        s = LowerCaseSet()
        s.update(['TKTK', 'tKtK', 'Tktk'])
        self.assertTrue('tktk' in s)
        self.assertEqual(len(s), 1)

    def test_contains(self):
        """make sure __contains__ casts things properly"""
        s = LowerCaseSet(['tktk'])
        self.assertTrue('TKTK' in s)
        self.assertTrue('Tktk' in s)
        self.assertTrue('tKtK' in s)
