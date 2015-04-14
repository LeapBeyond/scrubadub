import unittest

import scrubadub

from base import BaseTestCase


class UrlTestCase(unittest.TestCase, BaseTestCase):

    def test_http(self):
        """
        BEFORE: http://bit.ly/aser is neat
        AFTER:  {{URL}} is neat
        """
        self.compare_before_after()

    def test_https(self):
        """
        BEFORE: https://bit.ly/aser is neat
        AFTER:  {{URL}} is neat
        """
        self.compare_before_after()

    def test_www(self):
        """
        BEFORE: www.bit.ly/aser is neat
        AFTER:  {{URL}} is neat
        """
        self.compare_before_after()


    def test_long_url(self):
        """
        BEFORE: https://this.is/a/long?url=very#url is good
        AFTER:  {{URL}} is good
        """
        self.compare_before_after()

    def test_two_urls(self):
        """
        BEFORE: http://bit.ly/number-one http://www.google.com/two
        AFTER:  {{URL}} {{URL}}
        """
        self.compare_before_after()

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
