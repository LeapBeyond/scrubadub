import re

from textblob import TextBlob

from . import exceptions
from . import regexps


class Scrubber(object):
    """The Scrubber class is used to clean personal information out of
    dirty dirty text.
    """

    def clean_with_placeholders(self, text):
        """This is the master method that cleans all of the filth out of the
        dirty dirty ``text`` using the default options for all of the other
        ``clean_*`` methods below.
        """
        if not isinstance(text, unicode):
            raise exceptions.UnicodeRequired

        text = self.clean_proper_nouns(text)
        text = self.clean_email_addresses(text)
        text = self.clean_urls(text)
        return text

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
        dirty ``text``. This method also catches email addresses like ``john at
        gmail.com``.
        """
        for regex in regexps.EMAIL_REGEXS:
            text = regex.sub(replacement, text)
        return text

    def clean_urls(self, text, replacement="{{URL}}", keep_domain=False):
        """Use regular expressions to remove URLs that begin with ``http://``,
        `https://`` or ``www.`` from dirty dirty ``text``.

        With ``keep_domain=True``, this method only obfuscates the path on a
        URL, not its domain. For example,
        ``http://twitter.com/someone/status/234978haoin`` becomes
        ``http://twitter.com/{{replacement}}``.
        """
        for match in regexps.URL_REGEX.finditer(text):
            beg = match.start()
            end = match.end()
            if keep_domain:
                domain = match.group('domain')
                beg += len(domain)
            if beg < end:
                text = text.replace(match.string[beg:end], replacement)
        return text
