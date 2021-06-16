import string
import random

from faker import Faker

from .base import Filth


class AddressFilth(Filth):
    type = 'address'

    @staticmethod
    def _randomise_seperators(address: str) -> str:
        target = random.choice(["comma", "newline", "mixed", "spaces", "no_change"])
        if target == "comma":
            return address.replace('\n', ', ')
        elif target == "newline":
            return address.replace(', ', '\n')
        elif target == "spaces":
            return address.replace(', ', ' ').replace('\n', ' ')
        elif target == "mixed":
            address = address.replace(', ', '{{SEP}}').replace('\n', '{{SEP}}')
            while '{{SEP}}' in address:
                this_seporator = random.choice(["comma", "newline", "spaces"])
                if this_seporator == "comma":
                    address = address.replace('{{SEP}}', ', ', 1)
                elif this_seporator == "newline":
                    address = address.replace('{{SEP}}', '\n', 1)
                elif this_seporator == "spaces":
                    address = address.replace('{{SEP}}', ' ', 1)
            return address
        return address

    @staticmethod
    def _randomise_street_number(address: str) -> str:
        target = random.choice(["remove", "add_letter", "no_change", "no_change", "no_change", "no_change"])
        if target == "remove":
            address_split = address.split('\n')
            first_line_split = address_split[0].split(' ')
            try:
                int(first_line_split[0])
            except ValueError:
                return address
            new_first_line = " ".join(first_line_split[1:])
            return "\n".join([new_first_line] + address_split[1:])
        elif target == "add_letter":
            address_split = address.split('\n')
            first_line_split = address_split[0].split(' ')
            try:
                int(first_line_split[0])
            except ValueError:
                return address
            new_number = first_line_split[0] + random.choice(string.ascii_letters)
            new_first_line = " ".join([new_number] + first_line_split[1:])
            return "\n".join([new_first_line] + address_split[1:])
        return address

    @staticmethod
    def _randomise_postcode(address: str) -> str:
        target = random.choice(["remove", "lower", "no_change", "no_change", "no_change"])
        if target == "remove":
            return "\n".join(address.split('\n')[:-1])
        elif target == "lower":
            address_split = address.split('\n')
            return "\n".join(address.split('\n')[:-1] + [address_split[-1].lower()])
        return address

    @staticmethod
    def _randomise_country(address: str) -> str:
        target = random.choice(["country", "upper_country", "no_change", "no_change", "no_change"])
        if "country" in target:
            country = random.choice(['United Kingdom', 'Britain', 'England', 'Scotland', 'Wales', 'Cymru', 'GB'])
            if "upper" in target:
                country = country.upper()
            return address + "\n" + country
        return address

    @staticmethod
    def _randomise_building(address: str, faker: Faker) -> str:
        target = random.choice(["add_building", "no_change", "no_change", "no_change"])
        if target == "add_building":
            if bool(random.getrandbits(1)):
                building = faker.last_name() + " " + random.choice(["Building", "House", "Block"])
            else:
                building = random.choice(["Building", "House", "Block"]) + " " + faker.last_name()
            return building + "\n" + address
        return address

    @staticmethod
    def _randomise_case(address: str) -> str:
        target = random.random()
        if target >= 0.8:
            if target >= 0.9:
                address = address.upper()
            else:
                address = address.lower()
        return address

    @staticmethod
    def generate(faker: Faker) -> str:
        """Generates an example of this ``Filth`` type, usually using the faker python library.

        :param faker: The ``Faker`` class from the ``faker`` library
        :type faker: Faker
        :return: An example of this ``Filth``
        :rtype: str
        """
        address = faker.address()
        if faker.locales == ['en_GB']:
            address = AddressFilth._randomise_street_number(address)
            address = AddressFilth._randomise_building(address, faker)
            address = AddressFilth._randomise_postcode(address)
        if faker.locales == ['en_GB']:
            address = AddressFilth._randomise_country(address)
        address = AddressFilth._randomise_seperators(address)
        address = AddressFilth._randomise_case(address)

        return address
