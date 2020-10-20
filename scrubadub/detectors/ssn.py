import re

from .base import RegexDetector
from ..filth import SSNFilth


class SSNDetector(RegexDetector):
    """Use regular expression magic to remove social security numbers from
    dirty dirty ``text``.
    """

    filth_cls = SSNFilth
    name = 'ssn'

    # please note that this not only captures valid SSNs but also invalid ones.
    # This choice is delibrate in that we want to be biased toward replacing
    # any filth with a cleaner alternative.
    # https://en.wikipedia.org/wiki/Social_Security_number#Valid_SSNs
    regex = re.compile((
        r"[0-9][0-9][0-9]"       # first three digits
        r"[\-. ]"                # separator
        r"[0-9][0-9]"            # next two digits
        r"[\-. ]"                # separator
        r"[0-9][0-9][0-9][0-9]"  # last four digits
    ), re.VERBOSE)
