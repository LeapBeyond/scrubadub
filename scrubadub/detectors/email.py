import re

from .base import RegexDetector
from ..filth import EmailFilth


class EmailDetector(RegexDetector):
    """Use regular expression magic to remove email addresses from dirty
    dirty ``text``. This method also catches email addresses like ``john at
    gmail.com``.
    """
    filth_cls = EmailFilth
