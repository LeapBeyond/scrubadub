import re

from .base import RegexFilth


class SkypeFilth(RegexFilth):
    type = 'skype'

    # these two regular expressions are used to validate a skype usernames.
    # _TOKEN is the core regular expression that is used to chunk text into
    # tokens to make sure all valid skype usernames are considered the same
    # token. Importantly, the word "skype" must pass the _SKYPE regex.
    # SKYPE_TOKEN is used to tokenize text and SKYPE_USERNAME is the same thing
    # but with the 6-32 character limit imposed on the username. adapted from
    # http://bit.ly/1FQs1hD
    _SKYPE = r'[a-zA-Z][a-zA-Z0-9_\-\,\.]'
    SKYPE_TOKEN = re.compile(_SKYPE+'+')
    SKYPE_USERNAME = re.compile(_SKYPE+'{5,31}')
