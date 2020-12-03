import faker
import unittest

from scrubadub.filth import LocationFilth

class LocationFilthTestCase(unittest.TestCase):

    def test_generate(self):
        fake = faker.Faker()
        faker.Faker.seed(4321)

        self.assertEqual(
            'West Bryan',
            LocationFilth.generate(faker=fake),
        )
