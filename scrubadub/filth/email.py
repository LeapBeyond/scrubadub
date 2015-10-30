import re

from .base import RegexFilth


class EmailFilth(RegexFilth):
    type = 'email'

    # there may be better solutions than this out there and this certainly
    # doesn't do that great of a job with people that spell out the
    # hyphenation of their email address, but its a pretty solid start.
    #
    # adapted from https://gist.github.com/dideler/5219706
    regex = re.compile((
        "[a-z0-9!#$%&'*+\/=?^_`{|}~-]+"             # start with this character
        "(?:\.[a-z0-9!#$%&'*+\/=?^_`{|}~-]+)*"      # valid next characters
        "(@|\sat\s)"                                # @ or at fanciness
        "(?:"
        "[a-z0-9]"                                  # domain starts like this
        "(?:[a-z0-9-]*[a-z0-9])?"                   # might have this
        "(\.|\sdot\s)"                              # . or dot fanciness
        ")+"                                        # repeat as necessary
        "[a-z0-9](?:[a-z0-9-]*[a-z0-9])?"           # end of domain
    ), re.VERBOSE)
