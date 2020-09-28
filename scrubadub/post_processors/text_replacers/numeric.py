import os
import hashlib

from typing import Optional, Sequence, Type, List

from ...filth import Filth
from ... import utils
from ..base import PostProcessor


class NumericReplacer(PostProcessor):
    name = 'numbered_replacer'  # type: str

    # NOTE: this is not an efficient way to store this in memory. could
    # alternatively hash the type and text and do away with the overhead
    # bits of storing the tuple in the lookup
    lookup = utils.Lookup()

    def process_filth(self, filth_list: Sequence[Filth]) -> Sequence[Filth]:

        for filth_item in filth_list:
            filth_item.replacement_string = '{}-{:d}'.format(
                filth_item.type.upper(),
                self.lookup[(filth_item.type, filth_item.text.lower())]
            )

        return filth_list
