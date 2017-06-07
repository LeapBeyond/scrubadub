import re

import nltk
import textblob

from .base import RegexDetector
from ..filth import SkypeFilth


class SkypeDetector(RegexDetector):
    """Skype usernames tend to be used inline in dirty dirty text quite
    often but also appear as ``skype: {{SKYPE}}`` quite a bit. This method
    looks at words within ``word_radius`` words of "skype" for things that
    appear to be misspelled or have punctuation in them as a means to
    identify skype usernames.

    Default ``word_radius`` is 10, corresponding with the rough scale of
    half of a sentence before or after the word "skype" is used. Increasing
    the ``word_radius`` will increase the false positive rate and
    decreasing the ``word_radius`` will increase the false negative rate.
    """
    filth_cls = SkypeFilth

    word_radius = 10

    def iter_filth(self, text):

        # find 'skype' in the text using a customized tokenizer. this makes
        # sure that all valid skype usernames are kept as tokens and not split
        # into different words
        tokenizer = nltk.tokenize.regexp.RegexpTokenizer(
            self.filth_cls.SKYPE_TOKEN
        )
        blob = textblob.TextBlob(text, tokenizer=tokenizer)
        skype_indices, tokens = [], []
        for i, token in enumerate(blob.tokens):
            tokens.append(token)
            if 'skype' in token.lower():
                skype_indices.append(i)

        # go through the words before and after skype words to identify
        # potential skype usernames.
        skype_usernames = []
        for i in skype_indices:
            jmin = max(i-self.word_radius, 0)
            jmax = min(i+self.word_radius+1, len(tokens))
            for j in list(range(jmin, i)) + list(range(i+1, jmax)):
                token = tokens[j]
                if self.filth_cls.SKYPE_USERNAME.match(token):

                    # this token is a valid skype username. Most skype
                    # usernames appear to be misspelled words. Word.spellcheck
                    # does not handle the situation of an all caps word very
                    # well, so we cast these to all lower case before checking
                    # whether the word is misspelled
                    if token.isupper():
                        token = token.lower()
                    word = textblob.Word(token)
                    suggestions = word.spellcheck()
                    corrected_word, score = suggestions[0]
                    if score < 0.5:
                        skype_usernames.append(token)

        # replace all skype usernames
        if skype_usernames:
            self.filth_cls.regex = re.compile('|'.join(skype_usernames))
        else:
            self.filth_cls.regex = None
        return super(SkypeDetector, self).iter_filth(text)
