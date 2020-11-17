from faker import Faker

from .base import Filth


class UrlFilth(Filth):
    type = 'url'

    # This allows you to keep the domain
    keep_domain = False

    # this can be used to customize the output, particularly when
    # keep_domain=True
    url_placeholder = type.upper()

    @property
    def placeholder(self):
        if self.keep_domain:
            return self.match.group('domain') + self.url_placeholder
        return self.url_placeholder

    @staticmethod
    def generate(faker: Faker) -> str:
        """Generates an example of this ``Filth`` type, usually using the faker python library.

        :param faker: The ``Faker`` class from the ``faker`` library
        :type faker: Faker
        :return: An example of this ``Filth``
        :rtype: str
        """
        return faker.url()
