"""regular expressions go here to prevent the code from becoming a gigantic
scary regular expression that is difficult to understand.
"""

import re

# there may be better solutions than this out there and this certainly
# doesn't do that great of a job with people that spell out the
# hyphenation of their email address, but its a pretty solid start.
#
# adapted from https://gist.github.com/dideler/5219706
EMAIL = re.compile((
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

# this regular expression is convenient for captures the domain name
# and the path separately, which is useful for keeping the domain name
# but sanitizing the path altogether
URL = re.compile(r'''
    (?P<domain>
        (https?:\/\/(www\.)?|www\.)          # protocol http://, https://, www.
        [\-\w@:%\.\+~\#=]{2,256}\.[a-z]{2,6} # domain name
        /?                                   # can have a trailing slash
    )(?P<path>
        [\-\w@:%\+\.~\#?&/=]*                # rest of path, query, and hash
    )
''', re.VERBOSE)

# this regular expression searches for patterns like "username: root password:
# root" that tend to occur very frequently in text. This does not currently
# catch things like "username / password is root / root"
CREDENTIALS = re.compile(r'''
    (username|login|u:)\s*:?\s*    # username might have : and whitespace
    (?P<username>[\w\-\.@+]*)      # capture the username for replacement
    \s+                            # some whitespace between
    (password|pw|p:)\s*:?\s*       # password might have : and whitespace
    (?P<password>.*)               # password can be anything until end of line
''', re.MULTILINE | re.VERBOSE | re.IGNORECASE)

# these two regular expressions are used to validate a skype usernames. _TOKEN
# is the core regular expression that is used to chunk text into tokens to make
# sure all valid skype usernames are considered the same token. Importantly,
# the word "skype" must pass the _SKYPE regex. SKYPE_TOKEN is used to tokenize
# text and SKYPE_USERNAME is the same thing but with the 6-32 character limit
# imposed on the username. adapted from http://bit.ly/1FQs1hD
_SKYPE = r'[a-zA-Z][a-zA-Z0-9_\-\,\.]'
SKYPE_TOKEN = re.compile(_SKYPE+'+')
SKYPE_USERNAME = re.compile(_SKYPE+'{5,31}')
