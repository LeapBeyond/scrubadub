import re

from .base import RegexDetector
from ..filth import GBDriversFilth


class GBDriversDetector(RegexDetector):
    """Use regular expressions to detect UK driving licence numbers,
    Simple pattern matching, no checksum solution.
    """

    name = 'gbdrivers'
    filth_cls = GBDriversFilth
    # this regex is looking for UK driving licence numbers that follow a pattern, no checksum
    regex = re.compile(r'''([a-z,A-Z,9]{5}\s?)((?:\s*\d\s*){6}[a-z,A-Z,9]{2}\w{3})\s?(\d{2})''', re.IGNORECASE)
