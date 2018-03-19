import unittest

from base import BaseTestCase


class CredentialsTestCase(unittest.TestCase, BaseTestCase):

    def test_clean_root_root_combo(self):
        """
        BEFORE: username: root\npassword: root\n\n
        AFTER:  username: {{USERNAME}}\npassword: {{PASSWORD}}\n\n
        """
        self.compare_clean_before_after()

    def test_clean_whitespaceless(self):
        """
        BEFORE: username:root\npassword:crickets
        AFTER:  username:{{USERNAME}}\npassword:{{PASSWORD}}
        """
        self.compare_clean_before_after()

    def test_clean_colonless(self):
        """
        BEFORE: username root\npassword crickets
        AFTER:  username {{USERNAME}}\npassword {{PASSWORD}}
        """
        self.compare_clean_before_after()

    def test_clean_email_username(self):
        """sometimes there is no colon"""
        result = self.clean(u'username: joe@example.com\npassword moi')
        self.assertNotIn("joe@example.com", result, 'email username remains "%s"' % result)
        self.assertNotIn("moi", result, 'password remains "%s"' % result)

    def test_clean_alternate_keywords(self):
        """
        BEFORE: login snoop pw biggreenhat
        AFTER:  login {{USERNAME}} pw {{PASSWORD}}
        """
        self.compare_clean_before_after()

    def test_clean_singleletter_keywords(self):
        """
        BEFORE: u: snoop\np: biggreenhat
        AFTER:  u: {{USERNAME}}\np: {{PASSWORD}}
        """
        self.compare_clean_before_after()

    def test_clean_singleletter_keyword_exceptions(self):
        """Make sure that the single letter keywords do not make mistakes

        BEFORE: This is your problem
        AFTER:  This is your problem
        """
        self.compare_clean_before_after()

    def test_clean_camelcase_keywords(self):
        """
        BEFORE: UserName snoop PassWord biggreenhat
        AFTER:  UserName {{USERNAME}} PassWord {{PASSWORD}}
        """
        self.compare_clean_before_after()

    def test_scan_root_root_combo(self):
        """
        BEFORE: username: root\npassword: root\n\n
        AFTER:  credential
        """
        self.compare_scan_before_after()

    def test_scan_whitespaceless(self):
        """
        BEFORE: username:root\npassword:crickets
        AFTER:  credential
        """
        self.compare_scan_before_after()

    def test_scan_colonless(self):
        """
        BEFORE: username root\npassword crickets
        AFTER:  credential
        """
        self.compare_scan_before_after()

    def test_scan_email_username(self):
        """sometimes there is no colon"""
        result = self.clean(u'username: joe@example.com\npassword moi')
        self.assertNotIn("joe@example.com", result, 'email username remains "%s"' % result)
        self.assertNotIn("moi", result, 'password remains "%s"' % result)

    def test_scan_alternate_keywords(self):
        """
        BEFORE: login snoop pw biggreenhat
        AFTER:  credential
        """
        self.compare_scan_before_after()

    def test_scan_singleletter_keywords(self):
        """
        BEFORE: u: snoop\np: biggreenhat
        AFTER:  credential
        """
        self.compare_scan_before_after()

    def test_scan_singleletter_keyword_exceptions(self):
        """Make sure that the single letter keywords do not make mistakes

        BEFORE: This is your problem
        AFTER:
        """
        self.compare_scan_before_after()

    def test_scan_camelcase_keywords(self):
        """
        BEFORE: UserName snoop PassWord biggreenhat
        AFTER:  credential
        """
        self.compare_scan_before_after()
