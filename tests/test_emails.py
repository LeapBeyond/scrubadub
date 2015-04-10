import unittest

from base import BaseTestCase


class EmailTestCase(unittest.TestCase, BaseTestCase):

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
