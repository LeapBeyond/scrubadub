import unittest

import scrubadub

from base import BaseTestCase


class UrlTestCase(unittest.TestCase, BaseTestCase):

    def test_clean_http(self):
        """
        BEFORE: http://bit.ly/aser is neat
        AFTER:  {{URL}} is neat
        """
        self.compare_clean_before_after()

    def test_clean_https(self):
        """
        BEFORE: https://bit.ly/aser is neat
        AFTER:  {{URL}} is neat
        """
        self.compare_clean_before_after()

    def test_clean_www(self):
        """
        BEFORE: www.bit.ly/aser is neat
        AFTER:  {{URL}} is neat
        """
        self.compare_clean_before_after()

    def test_clean_long_url(self):
        """
        BEFORE: https://this.is/a/long?url=very#url is good
        AFTER:  {{URL}} is good
        """
        self.compare_clean_before_after()

    def test_clean_two_urls(self):
        """
        BEFORE: http://bit.ly/number-one http://www.google.com/two
        AFTER:  {{URL}} {{URL}}
        """
        self.compare_clean_before_after()

    def test_scan_http(self):
        """
        BEFORE: http://bit.ly/aser is neat
        AFTER:  url
        """
        self.compare_scan_before_after()

    def test_scan_https(self):
        """
        BEFORE: https://bit.ly/aser is neat
        AFTER:  url
        """
        self.compare_scan_before_after()

    def test_scan_www(self):
        """
        BEFORE: www.bit.ly/aser is neat
        AFTER:  url
        """
        self.compare_scan_before_after()

    def test_scan_long_url(self):
        """
        BEFORE: https://this.is/a/long?url=very#url is good
        AFTER:  url
        """
        self.compare_scan_before_after()

    def test_scan_two_urls(self):
        """
        BEFORE: http://bit.ly/number-one http://www.google.com/two
        AFTER:  url
        """
        self.compare_scan_before_after()


class UrlKeepDomainTestCase(unittest.TestCase, BaseTestCase):

    def setUp(self):
        scrubadub.filth.UrlFilth.keep_domain = True
        scrubadub.filth.UrlFilth.url_placeholder = 'path/to/something'
        scrubadub.filth.UrlFilth.prefix = ''
        scrubadub.filth.UrlFilth.suffix = ''
        super(UrlKeepDomainTestCase, self).setUp()

    def tearDown(self):
        scrubadub.filth.UrlFilth.keep_domain = False
        scrubadub.filth.UrlFilth.url_placeholder = 'URL'
        scrubadub.filth.UrlFilth.prefix = '{{'
        scrubadub.filth.UrlFilth.suffix = '}}'

    def test_clean_path_word_in_sentence(self):
        """
        BEFORE: Find jobs at http://facebook.com/jobs
        AFTER:  Find jobs at http://facebook.com/path/to/something
        """
        self.compare_clean_before_after()

    def test_clean_keep_domain(self):
        """
        BEFORE: http://public.com/this/is/very/private
        AFTER:  http://public.com/path/to/something
        """
        self.compare_clean_before_after()

    def test_clean_keep_domain_empty_path(self):
        """
        BEFORE: http://public.com/
        AFTER:  http://public.com/path/to/something
        """
        self.compare_clean_before_after()

    def test_scan_path_word_in_sentence(self):
        """
        BEFORE: Find jobs at http://facebook.com/jobs
        AFTER:  url
        """
        self.compare_scan_before_after()

    def test_scan_keep_domain(self):
        """
        BEFORE: http://public.com/this/is/very/private
        AFTER:  url
        """
        self.compare_scan_before_after()

    def test_scan_keep_domain_empty_path(self):
        """
        BEFORE: http://public.com/
        AFTER:  url
        """
        self.compare_scan_before_after()
