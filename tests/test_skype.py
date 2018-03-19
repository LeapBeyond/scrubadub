import unittest

from base import BaseTestCase


class SkypeTestCase(unittest.TestCase, BaseTestCase):

    def test_clean_inline_skype_name(self):
        """
        BEFORE: contact me on skype (dean.malmgren) to chat
        AFTER:  contact me on skype ({{SKYPE}}) to chat
        """
        self.compare_clean_before_after()

    def test_clean_pre_inline_skype_name(self):
        """
        BEFORE: i'm dean.malmgren on skype
        AFTER:  i'm {{SKYPE}} on skype
        """
        self.compare_clean_before_after()

    def test_clean_parenthetical_skype(self):
        """
        BEFORE: i'm on skype (dean.malmgren) or can be reached on my cell
        AFTER:  i'm on skype ({{SKYPE}}) or can be reached on my cell
        """
        self.compare_clean_before_after()

    def test_clean_skype_signature(self):
        """
        BEFORE: skype: dean.malmgren\nnerd
        AFTER:  skype: {{SKYPE}}\nnerd
        """
        self.compare_clean_before_after()

    def test_clean_skype_addition(self):
        """
        BEFORE: I have added you on Skype. My ID is dean.malmgren
        AFTER:  I have added you on Skype. My ID is {{SKYPE}}
        """
        self.compare_clean_before_after()

    def test_clean_skype_usernames(self):
        """test different skype username formats"""
        usernames = (
            "joecool",
            "joe,cool",
            "joe.cool",
            "joe-cool",
        )
        docstring_template = """
        BEFORE: My Skype is %s
        AFTER:  My Skype is {{SKYPE}}
        """
        for username in usernames:
            self.compare_clean_before_after(docstring_template % username)

    def test_clean_all_caps_words_nearby(self):
        """
        BEFORE: SCREAM to get my attention on Skype (dean.malmgren)
        AFTER:  SCREAM to get my attention on Skype ({{SKYPE}})
        """
        self.compare_clean_before_after()

    def test_scan_inline_skype_name(self):
        """
        BEFORE: contact me on skype (dean.malmgren) to chat
        AFTER:  skype
        """
        self.compare_scan_before_after()

    def test_scan_pre_inline_skype_name(self):
        """
        BEFORE: i'm dean.malmgren on skype
        AFTER:  skype
        """
        self.compare_scan_before_after()

    def test_scan_parenthetical_skype(self):
        """
        BEFORE: i'm on skype (dean.malmgren) or can be reached on my cell
        AFTER:  skype
        """
        self.compare_scan_before_after()

    def test_scan_skype_signature(self):
        """
        BEFORE: skype: dean.malmgren\nnerd
        AFTER:  skype
        """
        self.compare_scan_before_after()

    def test_scan_skype_addition(self):
        """
        BEFORE: I have added you on Skype. My ID is dean.malmgren
        AFTER:  skype
        """
        self.compare_scan_before_after()

    def test_scan_skype_usernames(self):
        """test different skype username formats"""
        usernames = (
            "joecool",
            "joe,cool",
            "joe.cool",
            "joe-cool",
        )
        docstring_template = """
        BEFORE: My Skype is %s
        AFTER:  skype
        """
        for username in usernames:
            self.compare_scan_before_after(docstring_template % username)

    def test_scan_all_caps_words_nearby(self):
        """
        BEFORE: SCREAM to get my attention on Skype (dean.malmgren)
        AFTER:  skype
        """
        self.compare_scan_before_after()
