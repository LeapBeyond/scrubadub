import re

from scrubadub.detectors.base import RegexDetector
from scrubadub.filth import NationalInsuranceNumberFilth


class NationalInsuranceNumberDetector(RegexDetector):
    """Use regular expressions to remove the UK National Insurance number (NINO),
    Simple pattern matching, no checksum solution.
    """

    name = 'national_insurance_number'
    filth_cls = NationalInsuranceNumberFilth
    # this regex is looking for NINO that does not begin with certain letters
    regex = re.compile(
        r'(?!BG)(?!GB)(?!NK)(?!KN)(?!TN)(?!NT)(?!ZZ)(?:[A-CEGHJ-PR-TW-Z][A-CEGHJ-NPR-TW-Z])(?:\s*\d\s*){6}[A-D]',
        re.IGNORECASE | re.VERBOSE
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
        language, region = cls.locale_split(locale)
        return region in ['GB']
