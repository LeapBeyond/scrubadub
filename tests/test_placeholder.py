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

    def _test_phone_numbers(self, *phone_numbers):
        for phone_number in phone_numbers:
            self.assertEqual(
                self.clean(u'My phone number is %s' % phone_number),
                u'My phone number is {{PHONE}}',
                'missing phone number "%s"' % phone_number,
            )

    def test_american_phone_number(self):
        """test american-style phone numbers"""
        self._test_phone_numbers(
            '1-312-515-2239',
            '+1-312-515-2239',
            '1 (312) 515-2239',
            '312-515-2239',
            '(312) 515-2239',
            '(312)515-2239',
        )

    def test_extension_phone_numbers(self):
        """test phone numbers with extensions"""
        self._test_phone_numbers(
            '312-515-2239 x12',
            '312-515-2239 ext. 12',
            '312-515-2239 ext.12',
        )

    def test_international_phone_numbers(self):
        """test international phone numbers"""
        self._test_phone_numbers(
            '+47 21 30 85 99',
            '+45 69 19 88 56',
            '+46 852 503 499',
            '+31 619 837 236',
            '+86 135 3727 4136',
            '+61267881324',
        )

    def test_multiple_phone_numbers(self):
        # running this through scrubadub.clean replaces 'reached at
        # 312.714.8142' with '{{EMAIL}}'. See issue
        scrubber = scrubadub.scrubbers.Scrubber()
        result = scrubber.clean_phone_numbers(
            u'I can be reached at 312.714.8142 (cell) or 773.415.7432 (office)'
        )
        self.assertEqual(
            result,
            u'I can be reached at {{PHONE}} (cell) or {{PHONE}} (office)',
            'problem with multiple phone numbers: \n %s' % result,
        )
