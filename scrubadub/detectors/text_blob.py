import re
import textblob

from textblob.blob import BaseBlob
from textblob.en.taggers import PatternTagger

from typing import Optional, Generator

from scrubadub.detectors.catalogue import register_detector
from .base import RegexDetector
from ..filth import NameFilth, Filth
from ..utils import CanonicalStringSet

# BaseBlob uses NLTKTagger as a pos_tagger, but it works wrong
BaseBlob.pos_tagger = PatternTagger()


@register_detector
class TextBlobNameDetector(RegexDetector):
    """Use part of speech tagging from textblob to clean proper nouns out of the dirty dirty
    ``text``. Disallow particular nouns by adding them to the ``NameDetector.disallowed_nouns`` set.
    """
    filth_cls = NameFilth
    name = 'text_blob_name'
    autoload = False

    disallowed_nouns = CanonicalStringSet(["skype"])

    def iter_filth(self, text, document_name: Optional[str] = None) -> Generator[Filth, None, None]:
        """Yields discovered filth in the provided ``text``.

        :param text: The dirty text to clean.
        :type text: str
        :param document_name: The name of the document to clean.
        :type document_name: str, optional
        :return: An iterator to the discovered :class:`Filth`
        :rtype: Iterator[:class:`Filth`]
        """

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
            yield from super(TextBlobNameDetector, self).iter_filth(text, document_name=document_name)
        return

    @classmethod
    def supported_locale(cls, locale: str) -> bool:
        """Returns true if this ``Detector`` supports the given locale.

        :param locale: The locale of the documents in the format: 2 letter lower-case language code followed by an
                       underscore and the two letter upper-case country code, eg "en_GB" or "de_CH".
        :type locale: str
        :return: ``True`` if the locale is supported, otherwise ``False``
        :rtype: bool
        """
        language, region = cls.locale_split(locale)

        # fr and de are possible through plugins, but need to be implemented on this end
        # https://github.com/sloria/textblob-fr and https://github.com/markuskiller/textblob-de
        return language in ['en', ]
