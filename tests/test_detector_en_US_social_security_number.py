import faker
import unittest
from scrubadub.filth import SocialSecurityNumberFilth

from base import BaseTestCase


class SSNTestCase(unittest.TestCase, BaseTestCase):

    def test_example(self):
        """
        BEFORE: My social security number is 726-60-2033
        AFTER:  My social security number is {{SOCIAL_SECURITY_NUMBER}}
        """
        self.compare_before_after()

    def test_hyphens(self):
        """
        BEFORE: My social security number is 109-99-6000
        AFTER:  My social security number is {{SOCIAL_SECURITY_NUMBER}}
        """
        self.compare_before_after()

    def test_dots(self):
        """
        BEFORE: My social security number is 109.99.6000
        AFTER:  My social security number is {{SOCIAL_SECURITY_NUMBER}}
        """
        self.compare_before_after()

    def test_spaces(self):
        """
        BEFORE: My social security number is 109 99 6000
        AFTER:  My social security number is {{SOCIAL_SECURITY_NUMBER}}
        """
        self.compare_before_after()

    def test_generate(self):
        fake = faker.Faker('en_US')
        faker.Faker.seed(4321)

        self.assertEqual(
            '818-09-2900',
            SocialSecurityNumberFilth.generate(faker=fake),
        )
