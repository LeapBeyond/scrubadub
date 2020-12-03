import faker
import unittest

from scrubadub.filth import OrganizationFilth

class OrganizationFilthTestCase(unittest.TestCase):

    def test_generate(self):
        fake = faker.Faker()
        faker.Faker.seed(4321)

        self.assertEqual(
            'Russell Inc',
            OrganizationFilth.generate(faker=fake),
        )
