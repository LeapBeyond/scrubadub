import re

from .base import RegexDetector
from ..filth import UKNinoFilth


class NINODetector(RegexDetector):
    """Use regular expressions to remove the UK National Insurance number (NINO),
    Simple pattern matching, no checksum solution.
    """

    name = 'uknino'
    filth_cls = UKNinoFilth
    # this regex is looking for NINO that does not begin with certain letters
    regex = re.compile(r'''
    (?!BG)(?!GB)(?!NK)(?!KN)(?!TN)(?!NT)(?!ZZ)(?:[A-CEGHJ-PR-TW-Z][A-CEGHJ-NPR-TW-Z])(?:\s*\d\s*){6}([A-D]|\s)''',
                       re.IGNORECASE)
