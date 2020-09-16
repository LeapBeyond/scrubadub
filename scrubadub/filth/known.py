from .base import Filth

import typing

class PredefinedFilth(Filth):
    type = 'predefined'

    def __init__(self, *args, comparison_type: typing.Optional[str] = None, **kwargs):
        super(PredefinedFilth, self).__init__(*args, **kwargs)
        self.comparison_type = comparison_type
