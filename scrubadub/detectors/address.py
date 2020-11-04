"""
This modules provides a detector for addresses.

It is based on the python package `pyap` and so only supports the countries that pyap supports: US, GB and CA.
The results from `pyap` are cross-checked using `pypostal`, which builds upon openvenues' `libpostal` library.
`libpostal` needs to be compiled from source and instructions are available at https://github.com/openvenues/pypostal
"""

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
from ..filth.address import AddressFilth, USAddressFilth, GBAddressFilth


class AddressDetector(Detector):
    ignored_words = ["COVERAGE"]
    minimum_address_sections = 4
    filth_cls = AddressFilth
    country = 'US'  # Relies on pyap. Only US, CA and GB are implemented
    match_pyap_postal_fields = {'region1': 'state'}  # type: Dict[str, str]
    name = 'address'

    def iter_filth(self, text, document_name: Optional[str] = None):
        addresses = pyap.parse(text, country=self.country)
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
                    document_name=document_name
                )


class GBAddressDetector(AddressDetector):
    country = 'GB'
    filth_cls = GBAddressFilth
    match_pyap_postal_fields = {}  # type: Dict[str, str]
    minimum_address_sections = 0
    name = 'gb_address'


class USAddressDetector(AddressDetector):
    country = 'US'
    filth_cls = USAddressFilth
    name = 'us_address'


register_detector(AddressDetector, autoload=False)
