import unittest

from base import BaseTestCase


class EmailTestCase(unittest.TestCase, BaseTestCase):

    def test_john_gmail(self):
        """
        BEFORE: My email is john@gmail.com
        AFTER:  My email is {{EMAIL}}
        """
        self.compare_before_after()

    def test_John_gmail(self):
        """
        BEFORE: My email is John@gmail.com
        AFTER:  My email is {{EMAIL}}
        """
        self.compare_before_after()

    def test_John1_example_com(self):
        """
        BEFORE: My email is John1@example.com
        AFTER:  My email is {{EMAIL}}
        """
        self.compare_before_after()

    def test_adam_example_info(self):
        """
        BEFORE: My email is adam80@example.info
        AFTER:  My email is {{EMAIL}}
        """
        self.compare_before_after()

    def test_uppercase(self):
        """
        BEFORE: My email is HELLO@EXAMPLE.COM
        AFTER:  My email is {{EMAIL}}
        """
        self.compare_before_after()

    def test_fancy_john_gmail(self):
        """
        BEFORE: My email is john at gmail.com
        AFTER:  My email is {{EMAIL}}
        """
        self.compare_before_after()
