import re

from scrubadub.detectors.catalogue import register_detector
from .base import RegionLocalisedRegexDetector
from ..filth.postalcode import PostalCodeFilth


@register_detector
class PostalCodeDetector(RegionLocalisedRegexDetector):
    """Detects postal codes, currently only British post codes are supported."""
    filth_cls = PostalCodeFilth
    name = 'postalcode'
    autoload = True
    region_regex = {
        # Informed by https://en.wikipedia.org/wiki/Postcodes_in_the_United_Kingdom#Validation
        # and validated against https://osdatahub.os.uk/downloads/open/CodePointOpen
        'GB': re.compile(r"""
            (
                # Girobank postcode
                (?:[gG][iI][rR] {0,}0[aA]{2})|
                (?:  # British Overseas Territories in usual format
                    (?:
                        [aA][sS][cC][nN]|
                        [sS][tT][hH][lL]|
                        [tT][dD][cC][uU]|
                        [bB][bB][nN][dD]|
                        [bB][iI][qQ][qQ]|
                        [fF][iI][qQ][qQ]|
                        [pP][cC][rR][nN]|
                        [sS][iI][qQ][qQ]|
                        [iT][kK][cC][aA]
                    )
                    \ {0,}1[zZ]{2}
                )|
                (?:  # British Overseas Territories in zip-code format
                    (KY[0-9]|MSR|VG|AI)[ -]{0,}[0-9]{4}
                )|
                # (?:  # Bermuda including this causes too many false positives, so excluded for now
                #     [a-zA-Z]{2}\ {0,}[0-9]{2}
                # )|
                (?:  # British Forces Post Office
                    [Bb][Ff][Pp][Oo]\ {0,}[0-9]{1,4}
                )|
                (?:  # Mainland British postcodes
                    (?:
                        (?:[Ww][Cc][0-9][abehmnprvwxyABEHMNPRVWXY])|
                        (?:[Ee][Cc][1-4][abehmnprvwxyABEHMNPRVWXY])|
                        (?:[Nn][Ww]1[Ww])|
                        (?:[Ss][Ee]1[Pp])|
                        (?:[Ss][Ww]1[abehmnprvwxyABEHMNPRVWXY])|
                        (?:[EeNnWw]1[a-hjkpstuwA-HJKPSTUW])|
                        (?:[BbEeGgLlMmNnSsWw][0-9][0-9]?)|
                        (?:[a-pr-uwyzA-PR-UWYZ][a-hk-yxA-HK-XY][0-9][0-9]?)
                    )
                    \ {0,}[0-9][abd-hjlnp-uw-zABD-HJLNP-UW-Z]{2}
                )
            )
        """, re.VERBOSE),
    }
