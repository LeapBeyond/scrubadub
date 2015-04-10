import unittest

import scrubadub

from base import BaseTestCase


class NameTestCase(unittest.TestCase, BaseTestCase):

    def test_john(self):
        """Make sure proper names are removed from the text"""
        self.assertEqual(
            self.clean(u'John is a cat'),
            u'{{NAME}} is a cat',
            'John not replaced with {{NAME}}',
        )
