import faker
import unittest
from scrubadub.filth import DoBFilth

import datetime
from base import BaseTestCase


class DoBTestCase(unittest.TestCase, BaseTestCase):

    def test_DoB_1(self):
        """
        BEFORE: My date of birth is 17/06/1976.
        AFTER:  My date of birth is {{DOB}}.
        """
        self.compare_before_after()

    def test_DoB_2(self):
        """
        BEFORE: Date of birth: 15 June 1991
        AFTER:  Date of birth: {{DOB}}
        """
        self.compare_before_after()

    def test_DoB_3(self):
        """
        BEFORE: DOB: 02.12.1979
        AFTER:  DOB: {{DOB}}
        """
        self.compare_before_after()

    def test_DoB_4(self):
        """
        BEFORE: The claimant's, d.o.b. is 4 June 1976
        AFTER:  The claimant's, d.o.b. is {{DOB}}
        """
        self.compare_before_after()

    def test_DoB_5(self):
        """
        BEFORE: 1985-01-01 is my birthday.
        AFTER:  {{DOB}} is my birthday.
        """
        self.compare_before_after()

    def test_generate(self):
        fake = faker.Faker()
        faker.Faker.seed(4321)

        self.assertEqual(
            datetime.date(1939, 7, 20),
            DoBFilth.generate(faker=fake),
        )
