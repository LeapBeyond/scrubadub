from faker import Faker

from .base import Filth
import datetime


class DoBFilth(Filth):
    type = 'dob'

    @staticmethod
    def generate(faker: Faker) -> datetime.date:
        """Generates an example of this ``Filth`` type, usually using the faker python library.

        :param faker: The ``Faker`` class from the ``faker`` library
        :type faker: Faker
        :return: An example of this ``Filth``
        :rtype: datetime.date
        """
        return faker.date_of_birth()
