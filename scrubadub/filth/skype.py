import re
from faker import Faker

from .base import Filth


class SkypeFilth(Filth):
    type = 'skype'

    @staticmethod
    def generate(faker: Faker) -> str:
        """Generates an example of this ``Filth`` type, usually using the faker python library.

        :param faker: The ``Faker`` class from the ``faker`` library
        :type faker: Faker
        :return: An example of this ``Filth``
        :rtype: str
        """
        username = ''
        while len(username) < 5:
            username = re.sub(r'(^[^a-zA-Z])|[^a-zA-Z0-9_\-\,\.]', '', faker.user_name())[:31]
        return username
