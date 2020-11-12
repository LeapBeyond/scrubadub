import re

from .base import RegexDetector
from ..filth import GBDriversFilth


class GBDriversDetector(RegexDetector):
    """Use regular expressions to remove the UK National Insurance number (NINO),
    Simple pattern matching, no checksum solution.
    """

    name = 'gbdrivers'
    filth_cls = GBDriversFilth
    # this regex is looking for NINO that does not begin with certain letters
    regex = re.compile(r"([a-z,A-Z,9]{5} *)\d{6}[a-z,A-Z,9]{2}\w{3}\s?(\d{2})?",
                       re.IGNORECASE | re.VERBOSE)
