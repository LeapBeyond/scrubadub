import unittest

import scrubadub


class PlaceholderTestCase(unittest.TestCase):

    def test_john(self):
        """Make sure proper names are removed from the text"""
        self.assertEqual(
            scrubadub.clean_with_placeholders(u'John is a cat'),
            u'{{NAME}} is a cat',
            'John not replaced with {{NAME}}',
        )

    def test_gmail_john(self):
        """Make sure email addresses are removed from text"""
        self.assertEqual(
            scrubadub.clean_with_placeholders(u'My email is john@gmail.com'),
            u'My email is {{EMAIL}}',
            'john@gmail.com is not replaced with {{EMAIL}}',
        )

    def test_fancy_gmail_john(self):
        """Make sure email addresses are removed from text"""
        self.assertEqual(
            scrubadub.clean_with_placeholders(u'My email is john at gmail.com'),
            u'My email is {{EMAIL}}',
            'john at gmail.com is not replaced with {{EMAIL}}',
        )
        self.assertEqual(
            scrubadub.clean_with_placeholders(u'My email is john AT gmail.com'),
            u'My email is {{EMAIL}}',
            'john AT gmail.com is not replaced with {{EMAIL}}',
        )

    def test_empty(self):
        """Make sure this returns an empty string"""
        self.assertEqual(
            scrubadub.clean_with_placeholders(u''),
            u'',
            'empty string is not preserved',
        )

    def test_not_unicode(self):
        """Make sure unicode works, too"""
        with self.assertRaises(scrubadub.exceptions.UnicodeRequired):
            scrubadub.clean_with_placeholders('John is a byte string')
