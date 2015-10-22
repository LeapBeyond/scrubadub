import re

from .. import exceptions
from ..filth import RegexFilth

class Detector(object):
    def iter_filth(self, text):
        raise NotImplementedError('must be overridden by base classes')


class RegexDetector(Detector):
    regex = None
    filth_cls = RegexFilth

    def iter_filth(self, text):
        # TEST that you can't use a normal Filth object with RegexDetector
        if not issubclass(self.filth_cls, RegexFilth):
            raise exceptions.UnexpectedFilth(
                'RegexFilth required for RegexDetector'
            )
        for match in self.regex.finditer(text):
            yield self.filth_cls(match)
