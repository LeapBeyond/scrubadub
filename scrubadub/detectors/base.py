import warnings
from typing import Optional, ClassVar, Type, Generator, Pattern

from .. import exceptions
from ..filth import Filth


class Detector(object):
    filth_cls = Filth  # type: ClassVar[Type[Filth]]
    name = 'detector'  # type: str

    def __init__(self, name: Optional[str] = None):
        if getattr(self, 'name', 'detector') == 'detector' and getattr(self, 'filth_cls', None) is not None:
            if getattr(self.filth_cls, 'type', None) is not None and type(self) != Detector:
                self.name = self.filth_cls.type
        if name is not None:
            self.name = name

    def iter_filth(self, text: str, document_name: Optional[str] = None) -> Generator[Filth, None, None]:
        raise NotImplementedError('must be overridden by base classes')


class RegexDetector(Detector):
    """Base class to match PII with a regex.

    This class requires that the ``filth_cls`` attribute be set to the class of the ``Filth`` that should be
    returned by this ``Detector``.

    .. code:: pycon
    >>> import re, scrubadub
    >>> class NewUrlDetector(scrubadub.detectors.base.Detector):
    >>>     name = 'new_url_detector'
    >>>     filth_cls = scrubadub.filth.url.UrlFilth
    >>>     regex = re.compile(r'https.*$', re.IGNORECASE)
    >>> scrubber = scrubadub.Scrubber()
    >>> scrubber.add_detector(NewUrlDetector())
    >>> text = u"This url will be found https://example.com"
    >>> scrubber.clean(text)
    """

    regex = None  # type: Optional[Pattern[str]]
    filth_cls = Filth  # type: ClassVar[Type[Filth]]

    def iter_filth(self, text: str, document_name: Optional[str] = None) -> Generator[Filth, None, None]:
        if not issubclass(self.filth_cls, Filth):
            raise TypeError(
                'filth_cls attribute of {} needs to be set to a subclass of the Filth class.'.format(self.__class__)
            )

        # Allow the regex to be in the detector as well  as the filth class
        if self.regex is None:
            warnings.warn('regex should be defined in the Detector and not in the Filth class', DeprecationWarning)
            if self.filth_cls.regex is not None:
                self.regex = self.filth_cls.regex

        if self.regex is None:
            raise ValueError('No regular expression has been specified for {}.'.format(self.__class__))

        for match in self.regex.finditer(text):
            yield self.filth_cls(match=match, detector_name=self.name, document_name=document_name)
