from faker import Faker

from .base import Filth


class PostalCodeFilth(Filth):
    type = "postalcode"

    @staticmethod
    def generate(faker: Faker) -> str:
        """Generates an example of this ``Filth`` type, usually using the faker python library.

        :param faker: The ``Faker`` class from the ``faker`` library
        :type faker: Faker
        :return: An example of this ``Filth``
        :rtype: str
        """
        # for en_US I expect we should pick between .zipcode() and .zipcode_plus4()
        # as postcode() for en_US only returns the 5 number zip code
        return faker.postcode()
