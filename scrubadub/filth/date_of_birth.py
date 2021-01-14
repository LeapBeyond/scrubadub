from faker import Faker

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
        return str(faker.date_of_birth())
