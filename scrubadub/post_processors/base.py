from typing import Optional, Sequence

from ..filth import Filth


class PostProcessor(object):
    name = 'post_processor'  # type: str
    autoload = False  # type: bool
    index = 10000  # type: int

    def __init__(self, name: Optional[str] = None):
        if name is not None:
            self.name = name

    def process_filth(self, filth_list: Sequence[Filth]) -> Sequence[Filth]:
        raise NotImplementedError('must be overridden by base classes')
