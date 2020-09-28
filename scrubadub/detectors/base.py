import warnings
from typing import Optional, ClassVar, Type, Union, Pattern

from .. import exceptions
from ..filth import Filth


class Detector(object):
    filth_cls = Filth  # type: ClassVar[Type[Filth]]
    name = 'detector'  # type: str

    def __init__(self, name: Optional[str] = None):
        if getattr(self, 'name', None) is None:
            self.name = self.filth_cls.type
        if name is not None:
            self.name = name

    def iter_filth(self, text: str, document_name: Optional[str] = None):
        raise NotImplementedError('must be overridden by base classes')


class RegexDetector(Detector):
    """Base class to match PII with a regex"""
    regex = None  # type: Optional[Pattern[str]]

    def iter_filth(self, text: str, document_name: Optional[str] = None):
        if not issubclass(self.filth_cls, Filth):
            raise exceptions.UnexpectedFilth(
                'Filth required for RegexDetector'
            )

        # Allow the regex to be in the detector as well  as the filth class
        if self.regex is None:
            warnings.warn('regex should be defined in the Detector and not in the Filth class', DeprecationWarning)
            if self.filth_cls.regex is not None:
                self.regex = self.filth_cls.regex

        if self.regex is None:
            print(self.regex, self.filth_cls.regex)
            raise ValueError('No regular expression has been specified for {}.'.format(self.__class__))

        for match in self.regex.finditer(text):
            yield self.filth_cls(match=match, detector_name=self.name, document_name=document_name)
