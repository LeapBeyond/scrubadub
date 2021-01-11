from faker import Faker

from scrubadub.filth.base import Filth


class NationalInsuranceNumberFilth(Filth):
    type = 'national_insurance_number'

    @staticmethod
    def generate(faker: Faker) -> str:
        """Generates an example of this ``Filth`` type, usually using the faker python library.

        :param faker: The ``Faker`` class from the ``faker`` library
        :type faker: Faker
        :return: An example of this ``Filth``
        :rtype: str
        """
        return faker.ssn()
