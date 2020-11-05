import re
import textblob

from textblob.blob import BaseBlob
from textblob.en.taggers import PatternTagger

from typing import Optional, Generator

from . import register_detector
from .base import RegexDetector
from ..filth import NameFilth, Filth
from ..utils import CanonicalStringSet

# BaseBlob uses NLTKTagger as a pos_tagger, but it works wrong
BaseBlob.pos_tagger = PatternTagger()


class TextBlobNameDetector(RegexDetector):
    """Use part of speech tagging to clean proper nouns out of the dirty dirty
    ``text``. Disallow particular nouns by adding them to the
    ``NameDetector.disallowed_nouns`` set.
    """
    filth_cls = NameFilth
    name = 'text_blob_name'

    disallowed_nouns = CanonicalStringSet(["skype"])

    def iter_filth(self, text, document_name: Optional[str] = None) -> Generator[Filth, None, None]:

        if not isinstance(self.disallowed_nouns, CanonicalStringSet):
            raise TypeError(
                'NameDetector.disallowed_nouns must be CanonicalStringSet'
            )

        # find the set of proper nouns using textblob.
        proper_nouns = set()
        blob = textblob.TextBlob(text)
        for word, part_of_speech in blob.tags:
            is_proper_noun = part_of_speech in ("NNP", "NNPS")
            if is_proper_noun and word.lower() not in self.disallowed_nouns:
                proper_nouns.add(word)

        # use a regex to replace the proper nouns by first escaping any
        # lingering punctuation in the regex
        # http://stackoverflow.com/a/4202559/564709
        if proper_nouns:
            re_list = []
            for proper_noun in proper_nouns:
                re_list.append(r'\b' + re.escape(str(proper_noun)) + r'\b')
            self.regex = re.compile('|'.join(re_list))
            for filth in super(TextBlobNameDetector, self).iter_filth(text, document_name=document_name):
                yield filth
        return


register_detector(TextBlobNameDetector, autoload=False)
