import re

from faker import Faker

from .base import Filth


class TwitterFilth(Filth):
    type = 'twitter'

    @staticmethod
    def generate(faker: Faker) -> str:
        """Generates an example of this ``Filth`` type, usually using the faker python library.

        :param faker: The ``Faker`` class from the ``faker`` library
        :type faker: Faker
        :return: An example of this ``Filth``
        :rtype: str
        """
        return '@' + re.sub(r'[^a-zA-Z0-9_]', '', faker.user_name())[:15]
