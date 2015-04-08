import re

from textblob import TextBlob

import exceptions


class Scrubber(object):
    """The Scrubber class is used to clean personal information out of
    dirty dirty text.
    """

    def clean_with_placeholders(self, text):
        """This is the master method that cleans all of the filth out of the
        dirty dirty ``text``.
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
        dirty ``text``, even accounting for super hyphen duper hyphen
        clever people that spell out the punctuation of their email
        addresses period

        adapted from http://stackoverflow.com/a/719543/564709
        """
        regexs = (
            r'\b[\w\.\+\-]+@[\w\-]+\.[\w\-\.]+\b',
            r'\b[\w\.\+\-]+ at [\w\-]+\.[\w\-\.]+\b',
            r'\b[\w\.\+\-]+ AT [\w\-]+\.[\w\-\.]+\b',
        )
        for regex in regexs:
            text = re.sub(regex, replacement, text)
        return text

    def clean_urls(self, text, replacement="{{URL}}"):
        """Use regular expressions to remove URLs that begin with ``http://``,
        `https://`` or ``www.`` from dirty dirty ``text``.
        """
        # need to make a copy of result here to make sure this works correctly
        result = text
        for match in re.finditer(r'(?P<domain_name>(https?:\/\/(www\.)?|www\.)[\-\w@:%\.\+~#=]{2,256}\.[a-z]{2,6}/)(?P<path>[\-\w@:%\+\.~#?&//=]*)', text):
#            replacement = match.group('domain_name') + 'PATH/TO/SOMETHING'
            result = result.replace(match.string[match.start():match.end()],
                                    replacement)
        return result
        
