import re
import stdnum.exceptions
import stdnum.us.ssn

from typing import Optional, Generator

from scrubadub.detectors.base import RegexDetector
from scrubadub.filth import Filth, SocialSecurityNumberFilth


class SocialSecurityNumberDetector(RegexDetector):
    """Use regular expressions to detect a social security number (SSN) in
    dirty dirty ``text``.
    """

    filth_cls = SocialSecurityNumberFilth
    name = 'social_security_number'
    regex = re.compile((
        r"[0-9][0-9][0-9]"       # first three digits
        r"[\-. ]"                # separator
        r"[0-9][0-9]"            # next two digits
        r"[\-. ]"                # separator
        r"[0-9][0-9][0-9][0-9]"  # last four digits
    ), re.VERBOSE)

    def __init__(self, *args, validate: bool = True, **kwargs):
        """Initialise the detector.

        :param validate: Validate the SSN using the the stdnum package
        :type validate: bool, default True
        :param name: Overrides the default name of the :class:``Detector``
        :type name: str, optional
        :param locale: The locale of the documents in the format: 2 letter lower-case language code followed by an
                       underscore and the two letter upper-case country code, eg "en_GB" or "de_CH".
        :type locale: str, optional
        """
        self.validate = validate
        super(SocialSecurityNumberDetector, self).__init__(*args, **kwargs)

    def iter_filth(self, text: str, document_name: Optional[str] = None) -> Generator[Filth, None, None]:
        for filth in super(SocialSecurityNumberDetector, self).iter_filth(text=text, document_name=document_name):
            if not self.validate:
                yield filth
            elif stdnum.us.ssn.is_valid(''.join(char for char in filth.text if char not in '. -')):
                yield filth

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
        return region in ['US']
