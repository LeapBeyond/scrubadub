import re

from .. import exceptions
from ..filth import Filth, RegexFilth


class Detector(object):
    filth_cls = None

    def iter_filth(self, text):
        raise NotImplementedError('must be overridden by base classes')


class RegexDetector(Detector):

    def iter_filth(self, text):
        if not issubclass(self.filth_cls, RegexFilth):
            raise exceptions.UnexpectedFilth(
                'RegexFilth required for RegexDetector'
            )
        if self.filth_cls.regex is None:
            return
        for match in self.filth_cls.regex.finditer(text):
            yield self.filth_cls(match)
