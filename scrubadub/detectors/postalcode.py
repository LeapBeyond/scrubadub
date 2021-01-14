import re

from .base import RegionLocalisedRegexDetector
from ..filth.postalcode import PostalCodeFilth


class PostalCodeDetector(RegionLocalisedRegexDetector):
    """Detects postal codes, currently only British post codes are supported."""
    filth_cls = PostalCodeFilth
    name = 'postalcode'
    region_regex = {
        'GB': re.compile(r"""
            (
                (?:[gG][iI][rR] {0,}0[aA]{2})|
                (?:
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
                (?:
                    (?:
                        (?:[a-pr-uwyzA-PR-UWYZ][a-hk-yxA-HK-XY]?[0-9][0-9]?)|
                        (?:
                            (?:[a-pr-uwyzA-PR-UWYZ][0-9][a-hjkstuwA-HJKSTUW])|
                            (?:[a-pr-uwyzA-PR-UWYZ][a-hk-yA-HK-Y][0-9][abehmnprv-yABEHMNPRV-Y])
                        )
                    )
                    \ {0,}[0-9][abd-hjlnp-uw-zABD-HJLNP-UW-Z]{2}
                )
            )
        """, re.VERBOSE),
    }
