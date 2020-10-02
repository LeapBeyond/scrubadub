import os
import hashlib

from typing import Sequence, Optional

from ...filth import Filth, MergedFilth
from ..base import PostProcessor


class FilthTypeReplacer(PostProcessor):
    name = 'filth_type_replacer'  # type: str

    @staticmethod
    def filth_label(filth, upper: bool = True, separator: Optional[str] = None) -> str:
        if separator is None:
            separator = '+'
        filths = [filth]
        if isinstance(filth, MergedFilth):
            filths = filth.filths
        label = separator.join([getattr(f, 'type', None) for f in filths if getattr(f, 'type', None) is not None])
        if upper:
            label = label.upper()
        return label

    def process_filth(self, filth_list: Sequence[Filth]) -> Sequence[Filth]:
        for filth_item in filth_list:
            filth_item.replacement_string = self.filth_label(filth_item)
        return filth_list


__all__ = ['FilthTypeReplacer']
