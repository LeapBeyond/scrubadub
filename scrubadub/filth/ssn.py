import re

from .base import RegexFilth


class SSNFilth(RegexFilth):
    type = 'ssn'

    # please note that this not only captures valid SSNs but also invalid ones.
    # This choice is delibrate in that we want to be biased toward replacing
    # any filth with a cleaner alternative.
    # https://en.wikipedia.org/wiki/Social_Security_number#Valid_SSNs
    regex = re.compile((
        "[0-9][0-9][0-9]"       # first three digits
        "[\-. ]"                # separator
        "[0-9][0-9]"            # next two digits
        "[\-. ]"                # separator
        "[0-9][0-9][0-9][0-9]"  # last four digits
    ), re.VERBOSE)
