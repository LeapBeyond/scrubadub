import random
import datetime
import dateparser
from faker import Faker

from .base import Filth


class DateOfBirthFilth(Filth):
    type = 'date_of_birth'
    min_age_years = 18
    max_age_years = 100

    @staticmethod
    def generate(faker: Faker) -> str:
        """Generates an example of this ``Filth`` type, usually using the faker python library.

        :param faker: The ``Faker`` class from the ``faker`` library
        :type faker: Faker
        :return: An example of this ``Filth``
        :rtype: str
        """
        formats = [
            '%c',  # Tue Aug 16 21:30:00 1988 (en_US); locale dependant
            '%x',  # 08/16/1988 (en_US); locale dependant
            '%a %d %b %Y',  # Sun 19 Jan 1999
            '%A %d %B %Y',  # Sunday 19 January 1999
            '%d-%m-%Y',  # 15-01-1999
            '%A %dth, %B, %Y',  # Monday 08th, January, 1973
        ]
        return faker.date_of_birth().strftime(random.choice(formats))

    def is_valid(self) -> bool:
        """Check to see if the found filth is valid."""
        found_date = dateparser.parse(self.text)
        if found_date is None:
            return False
        years_since_identified_date = datetime.date.today().year - found_date.year
        return DateOfBirthFilth.min_age_years <= years_since_identified_date <= DateOfBirthFilth.max_age_years
