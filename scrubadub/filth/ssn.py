import re

from .base import RegexFilth


class SSNFilth(RegexFilth):
    type = 'ssn'

    regex = re.compile((
        "[0-9][0-9][0-9]"       # first three digits
        "[\-. ]"                # separator
        "[0-9][0-9]"            # next two digits
        "[\-. ]"                # separator
        "[0-9][0-9][0-9][0-9]"  # last four digits
    ), re.VERBOSE)
