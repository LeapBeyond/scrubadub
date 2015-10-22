import re

from .base import RegexDetector
from ..filth import EmailFilth


class EmailDetector(RegexDetector):
    """Use regular expression magic to remove email addresses from dirty
    dirty ``text``. This method also catches email addresses like ``john at
    gmail.com``.
    """

    # there may be better solutions than this out there and this certainly
    # doesn't do that great of a job with people that spell out the
    # hyphenation of their email address, but its a pretty solid start.
    #
    # adapted from https://gist.github.com/dideler/5219706
    regex = re.compile((
        "[a-z0-9!#$%&'*+\/=?^_`{|}~-]+"             # start with this character
        "(?:\.[a-z0-9!#$%&'*+\/=?^_`{|}~-]+)*"      # can have any number of these
        "(@|\sat\s)"                                # @ or at fanciness
        "(?:"
        "[a-z0-9]"                                  # domain starts like this
        "(?:[a-z0-9-]*[a-z0-9])?"                   # might have this
        "(\.|\sdot\s)"                              # . or dot fanciness
        ")+"                                        # repeat as necessary
        "[a-z0-9](?:[a-z0-9-]*[a-z0-9])?"           # end of domain
    ))
    filth_cls = EmailFilth
