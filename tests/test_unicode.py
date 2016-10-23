import sys
import unittest

import scrubadub

from base import BaseTestCase

@unittest.skipIf(sys.version_info >= (3,0), "Test only needed in Python 2")
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

    def test_useful_error_message(self):
        try:
            self.clean('John is a byte string')
        except scrubadub.exceptions.UnicodeRequired as e:
            self.assertIn("scrubadub works best with unicode", str(e))
        else:
            self.fail('UnicodeRequired was not raised')
