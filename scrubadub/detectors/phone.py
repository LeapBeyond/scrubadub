import phonenumbers

from typing import Optional

from scrubadub.detectors.catalogue import register_detector
from .base import Detector
from ..filth import PhoneFilth


@register_detector
class PhoneDetector(Detector):
    """Remove phone numbers from dirty dirty ``text`` using
    `python-phonenumbers <https://github.com/daviddrysdale/python-phonenumbers>`_, a port of a
    Google project to correctly format phone numbers in text.

    Set the locale on the scrubber or detector to set the region used to search for valid phone numbers.
    If the locale is set to 'en_CA' Canadian numbers will be searched for, while setting the local to 'en_GB' searches
    for British numbers.
    """
    filth_cls = PhoneFilth
    name = 'phone'
    autoload = True

    def iter_filth(self, text, document_name: Optional[str] = None):
        """Yields discovered filth in the provided ``text``.

        :param text: The dirty text to clean.
        :type text: str
        :param document_name: The name of the document to clean.
        :type document_name: str, optional
        :return: An iterator to the discovered :class:`Filth`
        :rtype: Iterator[:class:`Filth`]
        """
        # create a copy of text to handle multiple phone numbers correctly
        for match in phonenumbers.PhoneNumberMatcher(text, self.region):
            yield PhoneFilth(
                beg=match.start,
                end=match.end,
                text=match.raw_string,
                detector_name=self.name,
                document_name=document_name,
                locale=self.locale,
            )

    @classmethod
    def supported_locale(cls, locale: str) -> bool:
        """Returns true if this ``Detector`` supports the given locale.

        :param locale: The locale of the documents in the format: 2 letter lower-case language code followed by an
                       underscore and the two letter upper-case country code, eg "en_GB" or "de_CH".
        :type locale: str
        :return: ``True`` if the locale is supported, otherwise ``False``
        :rtype: bool
        """
        return True
