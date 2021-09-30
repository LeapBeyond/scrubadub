import string
import stdnum.luhn
from faker import Faker

from .base import Filth


class CreditCardFilth(Filth):
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

    def is_valid(self) -> bool:
        return stdnum.luhn.is_valid(''.join(char for char in self.text if char in string.digits))
