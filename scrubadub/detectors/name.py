import re

import textblob

from .base import RegexDetector
from ..filth import NameFilth
from ..utils import CanonicalStringSet


class NameDetector(RegexDetector):
    """Use part of speech tagging to clean proper nouns out of the dirty dirty
    ``text``. Disallow particular nouns by adding them to the
    ``NameDetector.disallowed_nouns`` set.
    """
    filth_cls = NameFilth

    disallowed_nouns = CanonicalStringSet(["skype"])

    def iter_filth(self, text):

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
                re_list.append(r'\b' + re.escape(proper_noun) + r'\b')
            self.filth_cls.regex = re.compile('|'.join(re_list))
        else:
            self.filth_cls.regex = None
        return super(NameDetector, self).iter_filth(text)
