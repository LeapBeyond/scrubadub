import re

from textblob import TextBlob
import chardet


class Scrubber(object):
    """The Scrubber class is used to clean personal information out of
    dirty dirty text.
    """

    def decode(self, text):
        """Decode ``text`` using the `chardet
        <https://github.com/chardet/chardet>`_ package.
        """
        # only decode byte strings into unicode if it hasn't already
        # been done by a subclass
        if isinstance(text, unicode):
            return text

        # empty text? nothing to decode
        if not text:
            return u''

        # use chardet to automatically detect the encoding text. if chardet
        # doesn't know the answer, this will throw a rather ungraceful error
        max_confidence, max_encoding = 0.0, None
        result = chardet.detect(text)
        return text.decode(result['encoding'])

    def encode(self, text, encoding):
        """Encode the ``text`` in ``encoding`` byte-encoding. This ignores
        code points that can't be encoded in byte-strings.
        """
        return text.encode(encoding, 'ignore')

    def clean_with_placeholders(self, text):
        """This is the master method that cleans all of the filth out of the
        dirty dirty ``text``.
        """

        # decode the text as a unicode string as necessary
        text = self.decode(text)

        # do all the dirty work
        text = self.clean_proper_nouns(text)
        text = self.clean_email_addresses(text)

        # encode the unicode as a byte string
        return self.encode(text, 'utf-8')

    def clean_proper_nouns(self, text, replacement="{{NAME}}"):
        """Use part of speech tagging to clean proper nouns out of the dirty
        dirty ``text``.
        """

        # find the set of proper nouns using textblob
        proper_nouns = set()
        blob = TextBlob(text)
        for word, part_of_speech in blob.tags:
            if part_of_speech == "NNP" or part_of_speech == "NNPS":
                proper_nouns.add(word)

        # use a regex to replace the proper nouns by first escaping any
        # lingering punctuation in the regex
        # http://stackoverflow.com/a/4202559/564709
        for proper_noun in proper_nouns:
            proper_noun_re = r'\b' + re.escape(proper_noun) + r'\b'
            text = re.sub(proper_noun_re, replacement, text)
        return text

    def clean_email_addresses(self, text, replacement="{{EMAIL}}"):
        """Use regular expression magic to remove email addresses from dirty
        dirty ``text``
        """
        # some people are super hyphen duper hyphen clever and they
        # spell out the punctuation of their email addresses period
        #
        # adapted from http://stackoverflow.com/a/719543/564709
        regexs = (
            r'\b[\w\.\+\-]+@[\w\-]+\.[\w\-\.]+\b',
            r'\b[\w\.\+\-]+ at [\w\-]+\.[\w\-\.]+\b',
            r'\b[\w\.\+\-]+ AT [\w\-]+\.[\w\-\.]+\b',
        )
        for regex in regexs:
            text = re.sub(regex, replacement, text)
        return text
