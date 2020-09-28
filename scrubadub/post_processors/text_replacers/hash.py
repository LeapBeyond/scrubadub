import os
import hashlib

from typing import Optional, ClassVar, Sequence, List

from ...filth import Filth
from ..base import PostProcessor


class HashReplacer(PostProcessor):
    name = 'hash_replacer'  # type: str

    def __init__(self, length: Optional[int] = None, salt: Optional[str] = None, name: Optional[str] = None,
                 include_type: bool = True):
        super(HashReplacer, self).__init__(name=name)

        self.length = length or 16
        self.include_type = include_type
        if isinstance(salt, str):
            self.salt = salt.encode('utf8')
        else:
            self.salt = os.urandom(128)

    def process_filth(self, filth_list: Sequence[Filth]) -> Sequence[Filth]:
        for filth_item in filth_list:
            filth_item.replacement_string = ''
            if self.include_type:
                filth_item.replacement_string += filth_item.type + '-'
            filth_item.replacement_string += hashlib.pbkdf2_hmac(
                hash_name='sha256',
                password=filth_item.text.encode('utf8'),
                salt=self.salt,
                iterations=100000,
                dklen=self.length,
            ).hex()
            filth_item.replacement_string = filth_item.replacement_string.upper()
        return filth_list
