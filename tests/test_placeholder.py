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
            u'{{URL}} is neat',
            'http url is not replaced with {{URL}}',
        )

    def test_https(self):
        """https:// should be replaced"""
        self.assertEqual(
            self.clean(u'https://bit.ly/aser is neat'),
            u'{{URL}} is neat',
            'http url is not replaced with {{URL}}',
        )

    def test_www(self):
        """www. should be replaced"""
        self.assertEqual(
            self.clean(u'www.bit.ly/aser is neat'),
            u'{{URL}} is neat',
            'http url is not replaced with {{URL}}',
        )

    def test_long_url(self):
        """long url with query string and hash"""
        self.assertEqual(
           self.clean(u'https://this.is/a/long?url=very#url is good'),
           u'{{URL}} is good',
           "long urls aren't working properly"
        )

    def test_two_urls(self):
        """does this work with two URLs"""
        self.assertEqual(
           self.clean(u'http://bit.ly/number-one http://www.google.com/two'),
           u'{{URL}} {{URL}}',
           "multiple URLs aren't working properly",
        )

    def test_keep_domain(self):
        """keep_domain test with non-empty path"""
        scrubber = scrubadub.scrubbers.Scrubber()
        url = u'http://public.com/path/to/something/private'
        self.assertEqual(
            scrubber.clean_urls(url, replacement="{{PATH}}", keep_domain=True),
            u'http://public.com/{{PATH}}',
            'scrubber not replacing url path properly',
        )

    def test_keep_domain_empty_path(self):
        """keep_domain test with empty path"""
        scrubber = scrubadub.scrubbers.Scrubber()
        url = u'http://public.com/'
        self.assertEqual(
            scrubber.clean_urls(url, replacement="{{PATH}}", keep_domain=True),
            url,
            'scrubber with keep_domain is not handling an empty path well'
        )
