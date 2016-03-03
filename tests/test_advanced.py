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
