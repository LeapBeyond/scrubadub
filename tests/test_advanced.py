import unittest

from base import BaseTestCase


class AdvancedTestCase(unittest.TestCase, BaseTestCase):

    def test_disable_email(self):
        """
        BEFORE: contact Joe Duffy at joe@example.com
        AFTER:  contact {{NAME}} {{NAME}} at joe@example.com
        """
        before, after = self.get_before_after()
        import scrubadub
        scrubber = scrubadub.Scrubber()
        scrubber.remove_detector('email')
        self.check_equal(after, scrubber.clean(before))

    def test_customize_filth_identification(self):
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
