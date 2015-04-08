import unittest

import scrubadub


class PlaceholderTestCase(unittest.TestCase):

    def clean(self, text):
        return scrubadub.clean_with_placeholders(text)

    def test_john(self):
        """Make sure proper names are removed from the text"""
        self.assertEqual(
            self.clean(u'John is a cat'),
            u'{{NAME}} is a cat',
            'John not replaced with {{NAME}}',
        )

    def test_gmail_john(self):
        """Make sure email addresses are removed from text"""
        self.assertEqual(
            self.clean(u'My email is john@gmail.com'),
            u'My email is {{EMAIL}}',
            'john@gmail.com is not replaced with {{EMAIL}}',
        )

    def test_fancy_gmail_john(self):
        """Make sure email addresses are removed from text"""
        self.assertEqual(
            self.clean(u'My email is john at gmail.com'),
            u'My email is {{EMAIL}}',
            'john at gmail.com is not replaced with {{EMAIL}}',
        )
        self.assertEqual(
            self.clean(u'My email is john AT gmail.com'),
            u'My email is {{EMAIL}}',
            'john AT gmail.com is not replaced with {{EMAIL}}',
        )

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


    def test_http(self):
        """http:// should be replaced"""
        self.assertEqual(
            self.clean(u'http://bit.ly/aser is neat'),
            '{{URL}} is neat',
            'http url is not replaced with {{URL}}',
        )

    def test_https(self):
        """https:// should be replaced"""
        self.assertEqual(
            self.clean(u'https://bit.ly/aser is neat'),
            '{{URL}} is neat',
            'http url is not replaced with {{URL}}',
        )

    def test_www(self):
        """www. should be replaced"""
        self.assertEqual(
            self.clean(u'www.bit.ly/aser is neat'),
            '{{URL}} is neat',
            'http url is not replaced with {{URL}}',
        )
