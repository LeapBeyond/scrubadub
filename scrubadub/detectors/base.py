import re

from .. import exceptions
from ..filth import Filth, RegexFilth


class Detector(object):
    filth_cls = None

    def iter_filth(self, text):
        raise NotImplementedError('must be overridden by base classes')


class RegexDetector(Detector):
    """Base class to match PII with a regex"""
    regex = None

    def iter_filth(self, text):
        if not issubclass(self.filth_cls, RegexFilth):
            raise exceptions.UnexpectedFilth(
                'RegexFilth required for RegexDetector'
            )

        # Allow the regex to be in the detector as well
        # as the filth class
        if self.regex is None:
            if self.filth_cls.regex is None:
                return
            self.regex = self.filth_cls.regex
        for match in self.regex.finditer(text):
            yield self.filth_cls(match)
