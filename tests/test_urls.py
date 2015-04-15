import unittest

import scrubadub

from base import BaseTestCase


class UrlTestCase(unittest.TestCase, BaseTestCase):

    def check_keep_domain(self):
        """convenience method for runnint tests with the keep_domain kwarg"""
        before, after = self.get_before_after()
        scrubber = scrubadub.scrubbers.Scrubber()
        result = scrubber.clean_urls(
            before,
            replacement="path/to/something",
            keep_domain=True,
        )
        self.check_equal(after, result)

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

    def test_path_word_in_sentence(self):
        """
        BEFORE: Find jobs at http://facebook.com/jobs
        AFTER:  Find jobs at http://facebook.com/path/to/something
        """
        self.check_keep_domain()

    def test_keep_domain(self):
        """
        BEFORE: http://public.com/this/is/very/private
        AFTER:  http://public.com/path/to/something
        """
        self.check_keep_domain()

    def test_keep_domain_empty_path(self):
        """
        BEFORE: http://public.com/
        AFTER:  http://public.com/path/to/something
        """
        self.check_keep_domain()
