import re
try:
    import pyap
    import postal.parser
except (ImportError, ):
    raise ImportError(
        'To use scrubadub.detectors.address extra dependancies need to be installed.\n'
        'Please run: pip install scrubadub[address]'
    )


from typing import Dict, Optional

from . import register_detector
from .base import Detector
from ..filth.address import AddressFilth


class AddressDetector(Detector):
    """This ``Detector`` aims to detect addresses.

    This detector uses some complex dependencies and so is not enabled by default. To install the needed python
    dependencies run:

    .. code-block:: bash

        pip install scrubadub[address]

    This detector is based on the python package `pyap <https://pypi.org/project/pyap/>`_ and so only supports the
    countries that pyap supports: US, GB and CA. The results from `pyap` are cross-checked using
    `pypostal <https://github.com/openvenues/pypostal>`_, which builds upon openvenues'
    `libpostal <https://github.com/openvenues/libpostal>`_ library. libpostal needs to be compiled from source and
    instructions can be found on on their github `<https://github.com/openvenues/libpostal>`_

    After installing the python dependencies and libpostal, you can use this detector like so:

    >>> import scrubadub, scrubadub.detectors.address
    >>> scrubber = scrubadub.Scrubber()
    >>> scrubber.add_detector(scrubadub.detectors.address.AddressDetector)
    >>> scrubber.clean("I live at 6919 Bell Drives, East Jessicastad, MO 76908")
    'I live at {{ADDRESS}}'

    """
    filth_cls = AddressFilth
    name = 'address'
    ignored_words = ["COVERAGE"]

    def __init__(self, *args, **kwargs):
        """Initialise the ``Detector``.

        :param name: Overrides the default name of the :class:``Detector``
        :type name: str, optional
        :param locale: The locale of the documents in the format: 2 letter lower-case language code followed by an
                       underscore and the two letter upper-case country code, eg "en_GB" or "de_CH".
        :type locale: str, optional
        """
        super(AddressDetector, self).__init__(*args, **kwargs)

        self.match_pyap_postal_fields = {}  # type: Dict[str, str]
        self.minimum_address_sections = 0
        if self.region == 'US':
            self.match_pyap_postal_fields = {'region1': 'state'}
            self.minimum_address_sections = 4

    @classmethod
    def supported_locale(cls, locale: str) -> bool:
        """Returns true if this ``Detector`` supports the given locale.

        :param locale: The locale of the documents in the format: 2 letter lower-case language code followed by an
                       underscore and the two letter upper-case country code, eg "en_GB" or "de_CH".
        :type locale: str
        :return: ``True`` if the locale is supported, otherwise ``False``
        :rtype: bool
        """
        language, region = cls.locale_split(locale)
        return region in ['GB', 'CA', 'US']

    def iter_filth(self, text, document_name: Optional[str] = None):
        """Yields discovered filth in the provided ``text``.

        :param text: The dirty text to clean.
        :type text: str
        :param document_name: The name of the document to clean.
        :type document_name: str, optional
        :return: An iterator to the discovered :class:`Filth`
        :rtype: Iterator[:class:`Filth`]
        """
        addresses = pyap.parse(text, country=self.region)
        for address in addresses:
            # Ignore any addresses containing any explitally ignored words
            if any([word.lower() in address.full_address.lower() for word in self.ignored_words]):
                # print("contains an ignored word")
                continue

            postal_address = None
            if self.minimum_address_sections > 0:
                postal_address = postal.parser.parse_address(address.full_address)
                # Ensure that there are enough parts of the address to be a real address
                if len(postal_address) < self.minimum_address_sections:
                    # print("address too short")
                    continue

            if len(self.match_pyap_postal_fields) > 0:
                if postal_address is None:
                    postal_address = postal.parser.parse_address(address.full_address)
                # Check the two parses agree on part of the address
                for pyap_field, postal_field in self.match_pyap_postal_fields.items():
                    if not address.__getattribute__(pyap_field).lower() in [
                        part[0] for part in postal_address if part[1] == postal_field
                    ]:
                        continue

            # It seems to be a real address, lets look for it in the text
            # This is needed as pyap does some text normalisation, this undoes that normalisation
            # See _normalize_string() in https://github.com/vladimarius/pyap/blob/master/pyap/parser.py
            pattern = re.escape(address.full_address)
            pattern = pattern.replace(r',\ ', r'\s*([\n,]\s*)+')
            pattern = pattern.replace(r'\ ', r'\s+')
            pattern = pattern.replace('-', '[‐‑‒–—―]')
            pattern = r'\b' + pattern + r'\b'
            found_strings = re.finditer(pattern, text, re.MULTILINE | re.UNICODE)

            # Iterate over each found string matching this regex and yield some filth
            for instance in found_strings:
                yield self.filth_cls(
                    beg=instance.start(),
                    end=instance.end(),
                    text=instance.group(),
                    detector_name=self.name,
                    document_name=document_name,
                    locale=self.locale,
                )


register_detector(AddressDetector, autoload=False)
