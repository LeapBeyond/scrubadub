import re
import phonenumbers

from faker import Faker
from typing import List

from .base import Filth
from .. import utils


class PhoneFilth(Filth):
    type = 'phone'

    @staticmethod
    def generate(faker: Faker) -> str:
        """Generates an example of this ``Filth`` type, usually using the faker python library.

        :param faker: The ``Faker`` class from the ``faker`` library
        :type faker: Faker
        :return: An example of this ``Filth``
        :rtype: str
        """
        phone_number = ''
        language, region = utils.locale_split(faker._locales[0])
        results = []  # type: List[phonenumbers.PhoneNumberMatch]
        # Here I'm filtering for numbers that pass validation by the phonenumbers package
        while len(results) < 1:
            # Faker generates random numbers of the right format eg (###)###-####
            phone_number = re.sub(r'x.*$', '', faker.phone_number())
            # phonenumbers checks that they follow the rules around area codes and that they are possibly valid
            results = list(phonenumbers.PhoneNumberMatcher(phone_number, region))
        return phone_number
