import unittest

from scrubadub.utils import CanonicalStringSet

class CanonicalStringSetTestCase(unittest.TestCase):

    def test_init(self):
        """make sure that lower case casting works in __init__"""
        s = CanonicalStringSet(['TKTK', 'tKtK', 'Tktk'])
        self.assertTrue('tktk' in s)
        self.assertEqual(len(s), 1)

    def test_add(self):
        """make sure that lower case casting works in add"""
        s = CanonicalStringSet()
        s.add('TKTK')
        s.add('tKtK')
        s.add('Tktk')
        self.assertTrue('tktk' in s)
        self.assertEqual(len(s), 1)

    def test_update(self):
        """make sure lower case casting works in update"""
        s = CanonicalStringSet()
        s.update(['TKTK', 'tKtK', 'Tktk'])
        self.assertTrue('tktk' in s)
        self.assertEqual(len(s), 1)

    def test_update_again(self):
        """make sure udpate works properly"""
        s = CanonicalStringSet(['tktk'])
        s.update(set(['KtKt']))
        self.assertTrue('tktk' in s)
        self.assertTrue('ktkt' in s)
        self.assertIsInstance(s, CanonicalStringSet)

    def test_contains(self):
        """make sure __contains__ casts things properly"""
        s = CanonicalStringSet(['tktk'])
        self.assertTrue('TKTK' in s)
        self.assertTrue('Tktk' in s)
        self.assertTrue('tKtK' in s)

    def test_pop(self):
        """make sure pop deals with capitalized things properly"""
        s = CanonicalStringSet(['TKTK'])
        self.assertEqual(s.pop(), 'tktk')

    def test_remove(self):
        """make sure remove works properly"""
        s = CanonicalStringSet(['tktk'])
        s.remove('TKTK')
        self.assertFalse('tktk' in s)

    def test_discard(self):
        """make sure discard works properly"""
        s = CanonicalStringSet(['tktk'])
        s.discard('TKTK')
        s.discard('TkTk')
        s.discard('Tktk')
        self.assertFalse('tktk' in s)

    def test_non_string(self):
        """ensure error is thrown when non string is added"""
        s = CanonicalStringSet(['tktk'])
        s.add('123')
        with self.assertRaises(TypeError):
            s.add(123)
        with self.assertRaises(TypeError):
            s.add(None)

    # TODO: add more tests for all of the other set operations to make sure
    # people get what they expect
