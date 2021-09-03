import re

from scrubadub.detectors.catalogue import register_detector
from .base import RegexDetector
from ..filth import UrlFilth


@register_detector
class UrlDetector(RegexDetector):
    """Use regular expressions to remove URLs that begin with ``http://``,
    ``https://`` or ``www.`` from dirty dirty ``text``.

    With ``keep_domain=True``, this detector only obfuscates the path on a
    URL, not its domain. For example,
    ``http://twitter.com/someone/status/234978haoin`` becomes
    ``http://twitter.com/{{replacement}}``.
    """
    filth_cls = UrlFilth
    name = 'url'
    autoload = True

    # this regular expression is convenient for captures the domain name
    # and the path separately, which is useful for keeping the domain name
    # but sanitizing the path altogether
    regex = re.compile(r'''
        (?P<domain>
            (https?:\/\/(www\.)?|www\.)          # protocol http://, etc
            [\-\w@:%\.\+~\#=]{2,256}\.[a-z]{2,6} # domain name
            /?                                   # can have a trailing slash
        )(?P<path>
            [\-\w@:%\+\.~\#?&/=]*                # rest of path, query, & hash
        )
    ''', re.VERBOSE)
