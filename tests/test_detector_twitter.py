import unittest

from base import BaseTestCase


class EmailTestCase(unittest.TestCase, BaseTestCase):

    def test_email_and_twitter(self):
        """
        BEFORE: My email is john@gmail.com and i tweet at @john_gmail
        AFTER:  My email is {{EMAIL}} and i tweet at {{TWITTER}}
        """
        self.compare_before_after()

    def test_capitalise(self):
        """
        BEFORE: My tweeter is @John_gmail
        AFTER:  My tweeter is {{TWITTER}}
        """
        self.compare_before_after()

    def test_twitter(self):
        """
        BEFORE: This is an invalid handle @TwitterInfo
        AFTER:  This is an invalid handle @TwitterInfo
        """
        self.compare_before_after()

    def test_admin(self):
        """
        BEFORE: This is an invalid handle @XYZAdminInfo
        AFTER:  This is an invalid handle @XYZAdminInfo
        """
        self.compare_before_after()

    def test_uppercase(self):
        """
        BEFORE: My tweeter is @JOHN_JOHN123
        AFTER:  My tweeter is {{TWITTER}}
        """
        self.compare_before_after()

    def test_underscore(self):
        """
        BEFORE: My tweeter is @_JOHN_JOHN123
        AFTER:  My tweeter is {{TWITTER}}
        """
        self.compare_before_after()

    def test_underscores(self):
        """
        BEFORE: My tweeter is @_JOHN_JOHN123_
        AFTER:  My tweeter is {{TWITTER}}
        """
        self.compare_before_after()
