import unittest

from base import BaseTestCase


class CredentialsTestCase(unittest.TestCase, BaseTestCase):

    def test_root_root_combo(self):
        """username/password often split across adjacent lines"""
        result = self.clean(u'username: root\npassword: root\n\n')
        self.assertEqual(
            result,
            u'username: {{USERNAME}}\npassword: {{PASSWORD}}\n\n',
            'root/root combo not working: "%s"' % result,
        )

    def text_whitespaceless(self):
        """sometimes there's no whitespace"""
        result = self.clean(u'username:root\npassword:crickets')
        self.assertEqual(
            result,
            u'username:{{USERNAME}}\npassword:{{PASSWORD}}',
            'whitepace errors "%s"' % result,
        )

    def text_colonless(self):
        """sometimes there is no colon"""
        result = self.clean(u'username root\npassword crickets')
        self.assertEqual(
            result,
            u'username {{USERNAME}}\npassword {{PASSWORD}}',
            'whitepace errors "%s"' % result,
        )
