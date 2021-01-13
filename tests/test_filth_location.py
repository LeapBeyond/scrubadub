import faker
import unittest

from scrubadub.filth import LocationFilth

class LocationFilthTestCase(unittest.TestCase):

    def test_generate(self):
        class Faker:
            def city(self):
                return 'Brianland'

        self.assertEqual(
            'Brianland',
            LocationFilth.generate(faker=Faker()),
        )
