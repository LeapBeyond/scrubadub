import unittest

import scrubadub

from base import BaseTestCase

class UnicodeTestCase(unittest.TestCase, BaseTestCase):

    def test_empty(self):
        """Make sure this returns an empty string"""
        self.assertEqual(
            self.clean(u''),
            u'',
            'empty string is not preserved',
        )

    def test_not_unicode(self):
        """Make sure unicode works, too"""
        with self.assertRaises(scrubadub.exceptions.UnicodeRequired):
            self.clean('John is a byte string')
