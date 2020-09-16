from .base import Filth

import typing


class KnownFilth(Filth):
    type = 'known'

    def __init__(self, *args, comparison_type: typing.Optional[str] = None, **kwargs):
        super(KnownFilth, self).__init__(*args, **kwargs)
        self.comparison_type = comparison_type
