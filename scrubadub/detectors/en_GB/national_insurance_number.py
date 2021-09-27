import re

from scrubadub.detectors.catalogue import register_detector
from scrubadub.detectors.base import RegionLocalisedRegexDetector
from scrubadub.filth import NationalInsuranceNumberFilth


@register_detector
class NationalInsuranceNumberDetector(RegionLocalisedRegexDetector):
    """Use regular expressions to remove the GB National Insurance number (NINO),
    Simple pattern matching, no checksum solution.
    """
    name = 'national_insurance_number'
    autoload = True
    filth_cls = NationalInsuranceNumberFilth
    # this regex is looking for NINO that does not begin with certain letters
    region_regex = {
        'GB': re.compile(
            r'(?!BG)(?!GB)(?!NK)(?!KN)(?!TN)(?!NT)(?!ZZ)(?:[A-CEGHJ-PR-TW-Z][A-CEGHJ-NPR-TW-Z])(?:\s*\d\s*){6}[A-D]',
            re.IGNORECASE | re.VERBOSE
        ),
    }
