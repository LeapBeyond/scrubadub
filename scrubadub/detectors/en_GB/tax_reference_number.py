import re

from scrubadub.detectors.base import RegexDetector
from scrubadub.filth import TaxReferenceNumberFilth


class TaxReferenceNumberDetector(RegexDetector):
    """Use regular expressions to detect the UK PAYE temporary reference number (TRN),
    Simple pattern matching, no checksum solution.
    """

    name = 'tax_reference_number'
    filth_cls = TaxReferenceNumberFilth
    # this regex is looking for NINO that does not begin with certain letters
    regex = re.compile(r'''\d{2}\s?[a-zA-Z]{1}(?:\s*\d\s*){5}''', re.IGNORECASE)

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
