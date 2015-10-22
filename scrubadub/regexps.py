"""regular expressions go here to prevent the code from becoming a gigantic
scary regular expression that is difficult to understand.
"""

import re


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
