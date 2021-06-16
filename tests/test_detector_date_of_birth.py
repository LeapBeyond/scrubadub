import faker
import random
import unittest
import scrubadub
from scrubadub.filth import DateOfBirthFilth

import datetime
from base import BaseTestCase


class DoBTestCase(unittest.TestCase, BaseTestCase):


    def setUp(self):
        from scrubadub.detectors.date_of_birth import DateOfBirthDetector
        scrubadub.detectors.register_detector(DateOfBirthDetector, autoload=True)

    def tearDown(self) -> None:
        from scrubadub.detectors.date_of_birth import DateOfBirthDetector
        del scrubadub.detectors.detector_configuration[DateOfBirthDetector.name]

    def test_DoB_1(self):
        """
        BEFORE: My date of birth is 17/06/1976.
        AFTER:  My date of birth is {{DATE_OF_BIRTH}}.
        """
        self.compare_before_after()

    def test_DoB_2(self):
        """
        BEFORE: I was born 15th June 1991
        AFTER:  I was born {{DATE_OF_BIRTH}}
        """
        self.compare_before_after()

    def test_DoB_3(self):
        """
        BEFORE: DOB: 02.12.1979
        AFTER:  DOB: 02.12.{{DATE_OF_BIRTH}}
        """
        # TODO this is a known limitation of the dateparser search util,
        # TODO need to improve the search to include the full date
        self.compare_before_after()

    def test_DoB_4(self):
        """
        BEFORE: The claimant's, d.o.b. is 4 June 1976
        AFTER:  The claimant's, d.o.b. is {{DATE_OF_BIRTH}}
        """
        self.compare_before_after()

    def test_DoB_5(self):
        """
        BEFORE: 1985-01-01 is my birthday.
        AFTER:  {{DATE_OF_BIRTH}} is my birthday.
        """
        self.compare_before_after()

    def test_generate(self):
        fake = faker.Faker()
        faker.Faker.seed(4321)
        random.seed(4321)

        # I think this could fail just after midnight, because the generated date it relative to today's date and the
        # generated timedelta will unlikly be an integer number of days.
        # Will test and possibly remove/change this test further.
        self.assertIn(
            DateOfBirthFilth.generate(faker=fake),
            [
                (datetime.date.today() - datetime.timedelta(days=29729)).strftime('%a %d %b %Y'),
                (datetime.date.today() - datetime.timedelta(days=29729 + 1)).strftime('%a %d %b %Y'),
            ]
        )

    def test_init(self):
        from scrubadub.detectors.date_of_birth import DateOfBirthDetector
        with self.assertRaises(ValueError):
            DateOfBirthDetector(locale='zz_GB')

    def test_custom_words(self):
        from scrubadub.detectors.date_of_birth import DateOfBirthDetector
        detector = DateOfBirthDetector(context_words=['big day'])
        filths = list(detector.iter_filth('the big day is may 14th 1983\nsee you then'))

        self.assertEqual(1, len(filths))
        self.assertEqual(15, filths[0].beg)
        self.assertEqual(28, filths[0].end)
        self.assertEqual('may 14th 1983', filths[0].text)

    def test_young(self):
        from scrubadub.detectors.date_of_birth import DateOfBirthDetector
        detector = DateOfBirthDetector()
        filths = list(detector.iter_filth('my birthday is not may 14th 2020\nor may 15th 2020\nor +14-05-2020 23'))

        self.assertEqual(0, len(filths))
