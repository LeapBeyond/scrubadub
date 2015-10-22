import re

import textblob

from .base import RegexDetector
from ..filth import NameFilth


class NameDetector(RegexDetector):
    """Use part of speech tagging to clean proper nouns out of the dirty dirty
    ``text``. Disallow particular nouns by adding them to the
    ``NameDetector.disallowed_nouns`` set.
    """

    disallowed_nouns = set(["skype"])
    filth_cls = NameFilth

    def iter_filth(self, text):

        # find the set of proper nouns using textblob.
        disallowed_nouns = set(["skype"])
        proper_nouns = set()
        blob = textblob.TextBlob(text)
        for word, part_of_speech in blob.tags:
            is_proper_noun = part_of_speech in ("NNP", "NNPS")
            # TEST to make sure words added to disallowed_nouns are always
            # lowercase
            if is_proper_noun and word.lower() not in self.disallowed_nouns:
                proper_nouns.add(word)

        # use a regex to replace the proper nouns by first escaping any
        # lingering punctuation in the regex
        # http://stackoverflow.com/a/4202559/564709
        proper_noun_re_list = []
        for proper_noun in proper_nouns:
            proper_noun_re_list.append(r'\b' + re.escape(proper_noun) + r'\b')
        self.regex = re.compile('|'.join(proper_noun_re_list))
        return super(NameDetector, self).iter_filth(text)
