import faker
import unittest

from scrubadub.filth import OrganizationFilth

class OrganizationFilthTestCase(unittest.TestCase):

    def test_generate(self):
        fake = faker.Faker()
        faker.Faker.seed(4321)

        self.assertEqual(
            'Brown-Lindsey',
            OrganizationFilth.generate(faker=fake),
        )
