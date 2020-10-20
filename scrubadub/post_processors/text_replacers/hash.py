import os
import math
import hashlib

from typing import Optional, Sequence

from ...filth import Filth
from ..base import PostProcessor
from .filth_type import FilthTypeReplacer


class HashReplacer(PostProcessor):
    name = 'hash_replacer'  # type: str

    def __init__(self, length: Optional[int] = None, salt: Optional[str] = None, name: Optional[str] = None,
                 include_filth_type: bool = True):
        super(HashReplacer, self).__init__(name=name)

        self.length = length or 16
        self.include_type = include_filth_type
        if isinstance(salt, str):
            self.salt = salt.encode('utf8')
        else:
            self.salt = os.urandom(128)

    def process_filth(self, filth_list: Sequence[Filth]) -> Sequence[Filth]:
        for filth_item in filth_list:
            filth_item.replacement_string = ''
            if self.include_type:
                filth_item.replacement_string += FilthTypeReplacer.filth_label(filth_item) + '-'
            filth_item.replacement_string += hashlib.pbkdf2_hmac(
                hash_name='sha256',
                password=filth_item.text.encode('utf8'),
                salt=self.salt,
                iterations=100000,
                dklen=math.ceil(self.length/2),
            ).hex()[:self.length]
            filth_item.replacement_string = filth_item.replacement_string.upper()
        return filth_list


__all__ = ['HashReplacer']
