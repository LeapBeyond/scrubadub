from .base import RegexDetector
from ..filth import UrlFilth


class UrlDetector(RegexDetector):
    """Use regular expressions to remove URLs that begin with ``http://``,
    ``https://`` or ``www.`` from dirty dirty ``text``.

    With ``keep_domain=True``, this detector only obfuscates the path on a
    URL, not its domain. For example,
    ``http://twitter.com/someone/status/234978haoin`` becomes
    ``http://twitter.com/{{replacement}}``.
    """
    filth_cls = UrlFilth
