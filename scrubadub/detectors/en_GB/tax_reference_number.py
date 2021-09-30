import re

from scrubadub.detectors.catalogue import register_detector
from scrubadub.detectors.base import RegionLocalisedRegexDetector
from scrubadub.filth import TaxReferenceNumberFilth


@register_detector
class TaxReferenceNumberDetector(RegionLocalisedRegexDetector):
    """Use regular expressions to detect the UK PAYE temporary reference number (TRN),
    Simple pattern matching, no checksum solution.
    """

    name = 'tax_reference_number'
    autoload = True
    filth_cls = TaxReferenceNumberFilth
    # this regex is looking for NINO that does not begin with certain letters
    region_regex = {
        'GB': re.compile(r'''\d{2}\s?[a-zA-Z]{1}(?:\s*\d\s*){5}''', re.IGNORECASE),
    }
