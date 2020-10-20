import re

from .base import RegexDetector
from ..filth.postalcode import PostalCodeFilth


class PostalCodeDetector(RegexDetector):
    """Detects British postcodes"""
    filth_cls = PostalCodeFilth
    name = 'postalcode'
    postal_code_regexs = {
        'gb': re.compile(r"""
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

    def __init__(self, region='gb'):
        if region not in self.postal_code_regexs:
            raise NotImplementedError(
                'Postal code for region "{}" is not yet implemented, please choose one of: {}'.format(
                    region, list(self.postal_code_regexs.keys())
                )
            )
        self.regex = self.postal_code_regexs[region]
        super(PostalCodeDetector, self).__init__()
