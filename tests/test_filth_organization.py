import faker
import unittest

from scrubadub.filth import OrganizationFilth

class OrganizationFilthTestCase(unittest.TestCase):

    def test_generate(self):
        class Faker:
            def company(self):
                return 'Brown-Lindsey'

        self.assertEqual(
            'Brown-Lindsey',
            OrganizationFilth.generate(faker=Faker()),
        )
