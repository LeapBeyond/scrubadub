import re

from .base import RegexDetector
from ..filth import CredentialFilth
from scrubadub.detectors.catalogue import register_detector


@register_detector
class CredentialDetector(RegexDetector):
    """Remove username/password combinations from dirty drity ``text``.
    """
    filth_cls = CredentialFilth
    name = 'credential'
    autoload = True

    # this regular expression searches for patterns like
    #     "username: root password: root"
    # that tend to occur very frequently in text. This does not currently catch
    # things like "username / password is root / root"
    regex = re.compile(r'''
        (username|login|u:)\s*:?\s*    # username might have : and whitespace
        (?P<username>[\w\-\.@+]*)      # capture the username for replacement
        \s+                            # some whitespace between
        (password|pw|p:)\s*:?\s*       # password might have : and whitespace
        (?P<password>.*)               # password can be anything until EOL
    ''', re.MULTILINE | re.VERBOSE | re.IGNORECASE)
