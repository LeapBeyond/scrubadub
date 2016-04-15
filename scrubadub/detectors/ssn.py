import re

from .base import RegexDetector
from ..filth import SSNFilth


class SSNDetector(RegexDetector):
    """Use regular expression magic to remove social security numbers from
    dirty dirty ``text``.
    """

    filth_cls = SSNFilth
