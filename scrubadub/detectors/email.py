import re

from .base import RegexDetector
from ..filth import EmailFilth


class EmailDetector(RegexDetector):
    """Use regular expression magic to remove email addresses from dirty
    dirty ``text``. This method also catches email addresses like ``john at
    gmail.com``.
    """
    filth_cls = EmailFilth
    name = 'email'

    # there may be better solutions than this out there and this certainly
    # doesn't do that great of a job with people that spell out the
    # hyphenation of their email address, but its a pretty solid start.
    #
    # adapted from https://gist.github.com/dideler/5219706
    regex = re.compile((
        r"[a-z0-9!#$%&'*+\/=?^_`{|}~-]+"           # start with this character
        r"(?:\.[a-z0-9!#$%&'*+\/=?^_`{|}~-]+)*"    # valid next characters
        r"(@|\sat\s)"                              # @ or at fanciness
        r"(?:"
        r"[a-z0-9]"                                # domain starts like this
        r"(?:[a-z0-9-]*[a-z0-9])?"                 # might have this
        r"(\.|\sdot\s)"                            # . or dot fanciness
        r")+"                                      # repeat as necessary
        r"[a-z0-9](?:[a-z0-9-]*[a-z0-9])?"         # end of domain
    ), re.VERBOSE | re.IGNORECASE)
