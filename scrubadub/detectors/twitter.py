import re

from scrubadub.detectors.catalogue import register_detector
from .base import RegexDetector
from ..filth import TwitterFilth


@register_detector
class TwitterDetector(RegexDetector):
    """Use regular expression magic to remove twitter usernames from dirty
    dirty ``text``.
    """
    filth_cls = TwitterFilth
    name = 'twitter'
    autoload = True

    # https://help.twitter.com/en/managing-your-account/twitter-username-rules#error
    # Twitter user names must be 15 or less charachtors and only contain a-zA-Z0-9_
    # Twitter and admin are not allowed in user names
    # (?<!\w) prevents it matching email addresses
    regex = re.compile((
        r"(?<!\w)@((?!((admin)|(twitter)))[a-z0-9_]){2,15}\b"
    ), re.VERBOSE | re.IGNORECASE)
