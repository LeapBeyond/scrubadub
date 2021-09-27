import re

from scrubadub.detectors.catalogue import register_detector
from scrubadub.detectors.base import RegionLocalisedRegexDetector
from scrubadub.filth import SocialSecurityNumberFilth


@register_detector
class SocialSecurityNumberDetector(RegionLocalisedRegexDetector):
    """Use regular expressions to detect a social security number (SSN) in
    dirty dirty ``text``.
    """

    filth_cls = SocialSecurityNumberFilth
    name = 'social_security_number'
    autoload = True
    region_regex = {
        'US': re.compile((
            r"[0-9][0-9][0-9]"  # first three digits
            r"[\-. ]"  # separator
            r"[0-9][0-9]"  # next two digits
            r"[\-. ]"  # separator
            r"[0-9][0-9][0-9][0-9]"  # last four digits
        ), re.VERBOSE),
    }
