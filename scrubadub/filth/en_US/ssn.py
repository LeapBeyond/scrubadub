from faker import Faker
import stdnum.us.ssn

from scrubadub.filth.base import Filth


class SSNFilth(Filth):
    type = 'ssn'

    @staticmethod
    def generate(faker: Faker) -> str:
        """Generates an example of this ``Filth`` type, usually using the faker python library.

        :param faker: The ``Faker`` class from the ``faker`` library
        :type faker: Faker
        :return: An example of this ``Filth``
        :rtype: str
        """
        ssn = ''
        while not stdnum.us.ssn.is_valid(ssn):
            ssn = faker.ssn()
        return faker.ssn()
