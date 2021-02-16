from typing import Sequence, Optional

from ...filth import Filth, MergedFilth
from ..base import PostProcessor


class FilthRemover(PostProcessor):
    name = 'filth_remover'  # type: str

    def process_filth(self, filth_list: Sequence[Filth]) -> Sequence[Filth]:
        for filth_item in filth_list:
            filth_item.replacement_string = ''
        return filth_list

__all__ = ['FilthRemover']
