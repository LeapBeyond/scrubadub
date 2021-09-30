
import os
import math
import hashlib

from typing import Sequence, Optional, Union, Dict
from collections import defaultdict

from scrubadub.filth import Filth, MergedFilth, TaggedEvaluationFilth
from scrubadub.post_processors.base import PostProcessor
from scrubadub.post_processors.catalogue import register_post_processor
from scrubadub import utils


class FilthReplacer(PostProcessor):
    """Creates tokens that are used to replace the Filth found in the text of a document.

    This can be configured to include the filth type (eg phone, name, email, ...), a unique number for each piece of
    Filth, and a hash of the Filth.

    >>> import scrubadub
    >>> scrubber = scrubadub.Scrubber(post_processor_list=[
    ...     scrubadub.post_processors.FilthReplacer(),
    ... ])
    >>> scrubber.clean("Contact me at 522-368-8530 or hernandezjenna@example.com")
    'Contact me at PHONE or EMAIL'
    >>> scrubber = scrubadub.Scrubber(post_processor_list=[
    ...     scrubadub.post_processors.FilthReplacer(include_hash=True, hash_salt='example', hash_length=8),
    ... ])
    >>> scrubber.clean("Contact me at 522-368-8530 or hernandezjenna@example.com")
    'Contact me at PHONE-7358BF44 or EMAIL-AC0B8AC3'
    >>> scrubber = scrubadub.Scrubber(post_processor_list=[
    ...     scrubadub.post_processors.FilthReplacer(include_count=True),
    ... ])
    >>> scrubber.clean("Contact me at taylordaniel@example.com or hernandezjenna@example.com, "
    ...                "but taylordaniel@example.com is probably better.")
    'Contact me at EMAIL-0 or EMAIL-1, but EMAIL-0 is probably better.'
    """
    name = 'filth_replacer'  # type: str
    autoload = False
    index = 0

    # NOTE: this is not an efficient way to store this in memory. could
    # alternatively hash the type and text and do away with the overhead
    # bits of storing the tuple in the lookup
    typed_lookup = defaultdict(lambda: utils.Lookup(), {})  # type: Dict[str, utils.Lookup]

    def __init__(self, include_type: bool = True, include_count: bool = False, include_hash: bool = False,
                 uppercase: bool = True, separator: Optional[str] = None, hash_length: Optional[int] = None,
                 hash_salt: Optional[Union[str, bytes]] = None, **kwargs):
        """Initialise the FilthReplacer.

        :param include_type:
        :type include_type: bool, default True
        :param include_count:
        :type include_count: bool, default False
        :param include_hash:
        :type include_hash: bool, default False
        :param uppercase: Make the label uppercase
        :type uppercase: bool, default True
        :param separator: Used to separate labels if a merged filth is being replaced
        :type separator: Optional[str], default None
        :param hash_length: The length of the hexadecimal hash
        :type hash_length: Optional[int], default None
        :param hash_salt: The salt used in the hashing process
        :type hash_salt: Optional[Union[str, bytes]], default None
        """
        super(FilthReplacer, self).__init__(**kwargs)
        self.include_type = include_type
        self.include_count = include_count
        self.include_hash = include_hash
        self.uppercase = uppercase
        self.separator = separator or '+'
        self.hash_length = hash_length or 16

        if isinstance(hash_salt, str):
            self.hash_salt = hash_salt.encode('utf8')  # type: bytes
        else:
            self.hash_salt = os.urandom(128)

    @classmethod
    def reset_lookup(cls):
        """Reset the lookups that maintain a map of filth to a numeric ID."""
        cls.typed_lookup = defaultdict(lambda: utils.Lookup(), {})

    def filth_label(self, filth: Filth) -> str:
        """This function takes a filth and creates a label that can be used to replace the original text.

        :param filth: Limit the named entities to those in this list, defaults to ``{'PERSON', 'PER', 'ORG'}``
        :type filth: Filth
        :return: The replacement label that should be used for this `Filth`.
        :rtype: str

        """
        filths = [filth]
        if isinstance(filth, MergedFilth):
            filths = filth.filths

        replacements = set()
        for f in filths:
            replacement_pieces = []

            if self.include_type:
                filth_type = getattr(f, 'type', None)
                if filth_type is None:
                    continue
                if filth_type == TaggedEvaluationFilth.type:
                    filth_comparison_type = getattr(f, 'comparison_type', None)
                    if filth_comparison_type is not None:
                        filth_type += '_' + filth_comparison_type
                filth_type = filth_type.replace(' ', '_')

                replacement_pieces.append(filth_type)

            if self.include_count:
                replacement_pieces.append(str(FilthReplacer.typed_lookup[filth_type][f.text.lower()]))

            if self.include_hash:
                replacement_pieces.append(FilthReplacer.get_hash(f.text.lower(), self.hash_salt, self.hash_length))

            if len(replacement_pieces) == 0:
                replacement_pieces = ['filth']

            replacements.add('-'.join(replacement_pieces))

        label = self.separator.join(sorted(replacements))
        if self.uppercase:
            label = label.upper()
        return label

    @staticmethod
    def get_hash(text: str, salt: bytes, length: int) -> str:
        """Get a hash of some text, that has been salted and truncated.

        :param text: The text to be hashed
        :type text: str
        :param salt: The salt that should be used in this hashing
        :type salt: bytes
        :param length: The number of characters long that the hexadecimal hash should be
        :type length: int
        :return: The hash of the text
        :rtype: str
        """
        return hashlib.pbkdf2_hmac(
            hash_name='sha256',
            password=text.encode('utf8'),
            salt=salt,
            iterations=100000,
            dklen=math.ceil(length / 2),
        ).hex()[:length]

    def process_filth(self, filth_list: Sequence[Filth]) -> Sequence[Filth]:
        """Processes the filth to replace the original text

        :param filth_list: The text to be hashed
        :type filth_list: Sequence[Filth]
        :return: The processed filths
        :rtype: Sequence[Filth]
        """
        for filth_item in filth_list:
            filth_item.replacement_string = self.filth_label(filth=filth_item)

        return filth_list


register_post_processor(FilthReplacer)

__all__ = ['FilthReplacer']
