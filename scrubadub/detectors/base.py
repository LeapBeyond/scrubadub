import re
import warnings
from typing import Optional, ClassVar, Type, Generator, Pattern, Dict, Sequence

from ..filth import Filth
from ..import utils


class Detector(object):
    """This is the base class for all detectors.

    A simple example of how to make a new detector is given below:

    .. code:: pycon

        >>> import scrubadub
        >>> class MyFilth(scrubadub.filth.Filth):
        ...     type = 'mine'
        >>> class MyDetector(scrubadub.detectors.Detector):
        ...     name = 'my_fr_detector'
        ...     def iter_filth(self, text, document_name=None):
        ...         # This detector always returns this same Filth no matter the input.
        ...         # You should implement something better here.
        ...         yield MyFilth(beg=0, end=8, text='My stuff', document_name=document_name, detector_name=self.name)
        >>> scrubber = scrubadub.Scrubber()
        >>> scrubber.add_detector(MyDetector)
        >>> text = "My stuff can be found there."
        >>> scrubber.clean(text)
        '{{MINE}} can be found there.'

    You can also advertise a ``Detector`` as supporting a certain locale by defining the
    ```Detector.supported_local()``` function.
    """

    filth_cls = Filth  # type: ClassVar[Type[Filth]]
    name = 'detector'  # type: str
    autoload = False  # type: bool

    def __init__(self, name: Optional[str] = None, locale: str = 'en_US'):
        """Initialise the ``Detector``.

        :param name: Overrides the default name of the :class:``Detector``
        :type name: str, optional
        :param locale: The locale of the documents in the format: 2 letter lower-case language code followed by an
                       underscore and the two letter upper-case country code, eg "en_GB" or "de_CH".
        :type locale: str, optional
        """
        if getattr(self, 'name', 'detector') == 'detector' and getattr(self, 'filth_cls', None) is not None:
            if getattr(self.filth_cls, 'type', None) is not None and type(self) != Detector:
                self.name = self.filth_cls.type
                warnings.warn(
                    "Setting the detector name from the filth_cls.type is depreciated, please declare an explicit name"
                    "attribute on the class.",
                    DeprecationWarning
                )
        if name is not None:
            self.name = name

        self.locale = locale
        self.language, self.region = self.locale_split(locale)

        if hasattr(self, 'supported_locale'):
            if not self.supported_locale(locale=locale):  # type: ignore
                warnings.warn("Detector {} does not support the locale '{}'.".format(self.name, locale))

    locale_transform = staticmethod(utils.locale_transform)
    locale_split = staticmethod(utils.locale_split)

    def iter_filth(self, text: str, document_name: Optional[str] = None) -> Generator[Filth, None, None]:
        """Yields discovered filth in the provided ``text``.

        :param text: The dirty text to clean.
        :type text: str
        :param document_name: The name of the document to clean.
        :type document_name: str, optional
        :return: An iterator to the discovered :class:`Filth`
        :rtype: Iterator[:class:`Filth`]
        """
        raise NotImplementedError('must be implemented in derived classes')

    def iter_filth_documents(self, document_list: Sequence[str],
                             document_names: Sequence[Optional[str]]) -> Generator[Filth, None, None]:
        """Yields discovered filth in a list of documents.

        :param document_list: A list of documents to clean.
        :type document_list: List[str]
        :param document_names: A list containing the name of each document.
        :type document_names: List[str]
        :return: An iterator to the discovered :class:`Filth`
        :rtype: Iterator[:class:`Filth`]
        """
        raise NotImplementedError('must be implemented in derived classes')


class RegexDetector(Detector):
    """Base class to match PII with a regex.

    This class requires that the ``filth_cls`` attribute be set to the class of the ``Filth`` that should be
    returned by this ``Detector``.

    .. code:: pycon

        >>> import re, scrubadub
        >>> class NewUrlDetector(scrubadub.detectors.RegexDetector):
        ...     name = 'new_url_detector'
        ...     filth_cls = scrubadub.filth.url.UrlFilth
        ...     regex = re.compile(r'https.*$', re.IGNORECASE)
        >>> scrubber = scrubadub.Scrubber(detector_list=[NewUrlDetector()])
        >>> text = u"This url will be found https://example.com"
        >>> scrubber.clean(text)
        'This url will be found {{URL}}'
    """

    regex = None  # type: Optional[Pattern[str]]
    filth_cls = Filth  # type: ClassVar[Type[Filth]]

    def iter_filth(self, text: str, document_name: Optional[str] = None) -> Generator[Filth, None, None]:
        """Yields discovered filth in the provided ``text``.

        :param text: The dirty text to clean.
        :type text: str
        :param document_name: The name of the document to clean.
        :type document_name: str, optional
        :return: An iterator to the discovered :class:`Filth`
        :rtype: Iterator[:class:`Filth`]
        """
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
            yield self.filth_cls(match=match, detector_name=self.name, document_name=document_name,
                                 locale=self.locale)


class RegionLocalisedRegexDetector(RegexDetector):
    """Detector to detect ``Filth`` localised using regular expressions localised by the region"""
    region_regex = {}  # type: Dict[str, Pattern]

    def __init__(self, **kwargs):
        """Initialise the ``Detector``.

        :param name: Overrides the default name of the :class:``Detector``
        :type name: str, optional
        :param locale: The locale of the documents in the format: 2 letter lower-case language code followed by an
                       underscore and the two letter upper-case country code, eg "en_GB" or "de_CH".
        :type locale: str, optional
        """
        super(RegionLocalisedRegexDetector, self).__init__(**kwargs)

        # This will never be matched to anything.
        # It says anything where the next char is not an "a" character, but that is an "a".
        # This so the detector wont return filth if it doesn't have the region's correct regex.
        self.regex = re.compile(r'(?!a)a')

        if self.region in self.region_regex:
            self.regex = self.region_regex[self.region]

    @classmethod
    def supported_locale(cls, locale: str) -> bool:
        """Returns true if this ``Detector`` supports the given locale.

        :param locale: The locale of the documents in the format: 2 letter lower-case language code followed by an
                       underscore and the two letter upper-case country code, eg "en_GB" or "de_CH".
        :type locale: str
        :return: ``True`` if the locale is supported, otherwise ``False``
        :rtype: bool
        """
        language, region = cls.locale_split(locale)
        return region in cls.region_regex.keys()
