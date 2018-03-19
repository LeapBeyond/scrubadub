import unittest

from base import BaseTestCase


class AdvancedTestCase(unittest.TestCase, BaseTestCase):

    def test_clean_disable_email(self):
        """
        BEFORE: contact Joe Duffy at joe@example.com
        AFTER:  contact {{NAME}} {{NAME}} at joe@example.com
        """
        before, after = self.get_before_after()
        import scrubadub
        scrubber = scrubadub.Scrubber()
        scrubber.remove_detector('email')
        self.check_equal(after, scrubber.clean(before))

    def test_clean_customize_filth_identification(self):
        """
        BEFORE: contact Joe Duffy at joe@example.com
        AFTER:  contact <b>NAME</b> <b>NAME</b> at <b>EMAIL</b>
        """
        before, after = self.get_before_after()
        import scrubadub
        prefix = scrubadub.filth.base.Filth.prefix
        suffix = scrubadub.filth.base.Filth.suffix
        scrubadub.filth.base.Filth.prefix = u'<b>'
        scrubadub.filth.base.Filth.suffix = u'</b>'
        scrubber = scrubadub.Scrubber()
        self.check_equal(after, scrubber.clean(before))
        scrubadub.filth.base.Filth.prefix = prefix
        scrubadub.filth.base.Filth.suffix = suffix

    def test_clean_identifier(self):
        """
        BEFORE: i'm on skype (dean.malmgren) or can be reached at +1.800.346.1819
        AFTER:  i'm on skype ({{SKYPE-0}}) or can be reached at {{PHONE-1}}
        """
        self.compare_clean_before_after(replace_with='identifier')

    def test_clean_identifier_repeat(self):
        """
        BEFORE: my name is Dean Malmgren. Did I mention my name is Dean?
        AFTER:  my name is {{NAME-0}} {{NAME-1}}. Did I mention my name is {{NAME-0}}?
        """
        self.compare_clean_before_after(replace_with='identifier')

    def test_scan_multiple_matches(self):
        """
        BEFORE: i'm on skype (dean.malmgren) or can be reached at +1.800.346.1819 or at http://www.example.com/contact/me.html
        AFTER:  phone, skype, url
        """
        self.compare_scan_before_after()
