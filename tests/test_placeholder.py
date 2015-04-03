import unittest

import scrubadub


class PlaceholderTestCase(unittest.TestCase):

    def test_john(self):
        """Make sure proper names are removed from the text"""
        self.assertEqual(
            scrubadub.clean('John is a cat'),
            '{{NAME}} is a cat',
            'John not replaced with {{NAME}}',
        )

    def test_gmail_john(self):
        """Make sure email addresses are removed from text"""
        self.assertEqual(
            scrubadub.clean('My email is john@gmail.com'),
            'My email is {{EMAIL}}',
            'john@gmail.com is not replaced with {{EMAIL}}',
        )

    def test_fancy_gmail_john(self):
        """Make sure email addresses are removed from text"""
        self.assertEqual(
            scrubadub.clean('My email is john at gmail.com'),
            'My email is {{EMAIL}}',
            'john at gmail.com is not replaced with {{EMAIL}}',
        )
        self.assertEqual(
            scrubadub.clean('My email is john AT gmail.com'),
            'My email is {{EMAIL}}',
            'john AT gmail.com is not replaced with {{EMAIL}}',
        )
