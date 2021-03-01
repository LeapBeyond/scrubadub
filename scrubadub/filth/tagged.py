from .base import Filth

import typing


class TaggedEvaluationFilth(Filth):
    type = 'tagged'

    def __init__(self, *args, comparison_type: typing.Optional[str] = None, **kwargs):
        super(TaggedEvaluationFilth, self).__init__(*args, **kwargs)
        self.comparison_type = comparison_type
