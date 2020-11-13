import re

from .base import RegexDetector
from ..filth import GBTrnFilth


class GBTrnDetector(RegexDetector):
    """Use regular expressions to detect the UK PAYE temporary reference number (TRN),
    Simple pattern matching, no checksum solution.
    """

    name = 'gbtrn'
    filth_cls = GBTrnFilth
    # this regex is looking for NINO that does not begin with certain letters
    regex = re.compile(r'''\d{2}\s?[a-zA-Z]{1}(?:\s*\d\s*){5}''', re.IGNORECASE)
