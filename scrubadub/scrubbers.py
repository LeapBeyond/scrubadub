import re

from textblob import TextBlob
import phonenumbers

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

        # * phone numbers needs to come before email addresses (#8)
        # * credentials need to come before email addresses (#9)
        text = self.clean_proper_nouns(text)
        text = self.clean_urls(text)
        text = self.clean_phone_numbers(text)
        text = self.clean_credentials(text)
        text = self.clean_email_addresses(text)
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
        return regexps.EMAIL.sub(replacement, text)

    def clean_urls(self, text, replacement="{{URL}}", keep_domain=False):
        """Use regular expressions to remove URLs that begin with ``http://``,
        `https://`` or ``www.`` from dirty dirty ``text``.

        With ``keep_domain=True``, this method only obfuscates the path on a
        URL, not its domain. For example,
        ``http://twitter.com/someone/status/234978haoin`` becomes
        ``http://twitter.com/{{replacement}}``.
        """
        for match in regexps.URL.finditer(text):
            beg = match.start()
            end = match.end()
            if keep_domain:
                domain = match.group('domain')
                beg += len(domain)
            if beg < end:
                text = text.replace(match.string[beg:end], replacement)
        return text

    def clean_phone_numbers(self, text, replacement="{{PHONE}}", region="US"):
        """Remove phone numbers from dirty dirty ``text`` using
        `python-phonenumbers
        <https://github.com/daviddrysdale/python-phonenumbers>`, a port of a
        Google project to correctly format phone numbers in text.

        ``region`` specifies the best guess region to start with (default:
        ``"US"``). Specify ``None`` to only consider numbers with a leading
        ``+`` to be considered.
        """
        # create a copy of text to handle multiple phone numbers correctly
        result = text
        for match in phonenumbers.PhoneNumberMatcher(text, region):
            result = result.replace(text[match.start:match.end], replacement)
        return result

    def clean_credentials(self, text,
                          username_replacement="{{USERNAME}}",
                          password_replacement="{{PASSWORD}}"):
        """Remove username/password combinations from dirty drity ``text``.
        """
        position = 0
        while True:
            match = regexps.CREDENTIALS.search(text, position)
            if match:
                ubeg, uend = match.span('username')
                pbeg, pend = match.span('password')
                text = (
                    text[:ubeg] + username_replacement + text[uend:pbeg] +
                    password_replacement + text[pend:]
                )
                position = match.end()
            else:
                break
        return text
