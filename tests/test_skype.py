import unittest

from base import BaseTestCase


class SkypeTestCase(unittest.TestCase, BaseTestCase):

    def test_inline_skype_name(self):
        """
        BEFORE: contact me on skype at dean.malmgren to chat
        AFTER:  contact me on skype at {{SKYPE}} to chat
        """
        self.compare_before_after()

    def test_pre_inline_skype_name(self):
        """
        BEFORE: i'm dean.malmgren on skype
        AFTER:  i'm {{SKYPE}} on skype
        """
        self.compare_before_after()

    def test_parenthetical_skype(self):
        """
        BEFORE: i'm on skype (dean.malmgren) or can be reached on my cell
        AFTER:  i'm on skype ({{SKYPE}}) or can be reached on my cell
        """
        self.compare_before_after()

    def test_skype_signature(self):
        """
        BEFORE: skype: dean.malmgren\nnerd
        AFTER:  skype: {{SKYPE}}\nnerd
        """
        self.compare_before_after()
