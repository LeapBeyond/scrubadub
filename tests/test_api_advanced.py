import unittest

from base import BaseTestCase


class AdvancedTestCase(unittest.TestCase, BaseTestCase):

    def test_disable_email(self):
        """
        BEFORE: contact me at joe@example.com
        AFTER:  contact me at joe@example.com
        """
        before, after = self.get_before_after()
        import scrubadub
        scrubber = scrubadub.Scrubber()
        scrubber.remove_detector('email')
        self.check_equal(after, scrubber.clean(before))

    def test_customize_filth_identification(self):
        """
        BEFORE: contact me at joe@example.com
        AFTER:  contact me at <b>EMAIL</b>
        """
        before, after = self.get_before_after()
        import scrubadub
        prefix = scrubadub.filth.base.Filth.prefix
        suffix = scrubadub.filth.base.Filth.suffix
        scrubadub.filth.base.Filth.prefix = u'<b>'
        scrubadub.filth.base.Filth.suffix = u'</b>'
        try:
            scrubber = scrubadub.Scrubber()
            self.check_equal(after, scrubber.clean(before))
        finally:
            # Ensure that this is reset, no matter what happens above
            scrubadub.filth.base.Filth.prefix = prefix
            scrubadub.filth.base.Filth.suffix = suffix

    def test_identifier(self):
        """
        BEFORE: i'm on twitter (@john_smith) or can be reached at +1.800.346.1819
        AFTER:  i'm on twitter ({{TWITTER-0}}) or can be reached at {{PHONE-1}}
        """
        self.compare_before_after(replace_with='identifier')

    def test_identifier_repeat(self):
        """
        BEFORE: i'm on twitter (@john_smith), but tweet @john instead, don't tweet me @john_smith.
        AFTER:  i'm on twitter ({{TWITTER-0}}), but tweet {{TWITTER-1}} instead, don't tweet me {{TWITTER-0}}.
        """
        self.compare_before_after(replace_with='identifier')
