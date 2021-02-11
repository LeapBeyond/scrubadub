from faker import Faker
import random

from .base import Filth


class DateOfBirthFilth(Filth):
    type = 'date_of_birth'

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
