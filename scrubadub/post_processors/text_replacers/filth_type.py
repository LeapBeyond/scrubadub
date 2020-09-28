import os
import hashlib

from typing import Optional, ClassVar, Sequence, List

from ...filth import Filth
from ..base import PostProcessor


class FilthTypeReplacer(PostProcessor):
    name = 'filth_type_replacer'  # type: str

    def process_filth(self, filth_list: Sequence[Filth]) -> Sequence[Filth]:
        for filth_item in filth_list:
            filth_item.replacement_string = filth_item.type
        return filth_list
