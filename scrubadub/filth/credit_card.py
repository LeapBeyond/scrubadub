from faker import Faker

from .base import RegexFilth


class CreditCardFilth(RegexFilth):
    type = 'credit_card'

    @staticmethod
    def generate(faker: Faker) -> str:
        """Generates an example of this ``Filth`` type, usually using the faker python library.

        :param faker: The ``Faker`` class from the ``faker`` library
        :type faker: Faker
        :return: An example of this ``Filth``
        :rtype: str
        """
        return faker.credit_card_number()
