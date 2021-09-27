import re

from typing import Optional, Generator

from scrubadub.detectors.catalogue import register_detector
from .base import RegexDetector
from ..filth import EmailFilth, Filth


@register_detector
class EmailDetector(RegexDetector):
    """Use regular expression magic to remove email addresses from dirty
    dirty ``text``. This method also catches email addresses like ``john at
    gmail.com``.
    """
    filth_cls = EmailFilth
    name = 'email'
    autoload = True

    # there may be better solutions than this out there and this certainly
    # doesn't do that great of a job with people that spell out the
    # hyphenation of their email address, but its a pretty solid start.
    #
    # adapted from https://gist.github.com/dideler/5219706
    regex = re.compile((
        r"\b[a-z0-9!#$%&'*+\/=?^_`{|}~-]"             # start with this character
        r"(?:"
        r"    [\.a-z0-9!#$%&'*+\/=?^_`{|}~-]{0,62}"   # valid next characters (max length 64 chars before @)
        r"    [a-z0-9!#$%&'*+\/=?^_`{|}~-]"           # end with this character
        r")?"
        r"(?:@|\sat\s)"                               # @ or the word 'at' instead
        r"[a-z0-9]"                                   # domain starts like this
        r"(?:"
        r"    (?=[a-z0-9-]*(\.|\sdot\s))"             # A lookahead to ensure there is a dot in the domain
        r"    (?:\.|\sdot\s|[a-z0-9-]){0,251}"        # might have a '.' or the word 'dot' instead
        r"    [a-z0-9]"                               # domain has max 253 chars, ends with one of these
        r")+\b"
    ), re.VERBOSE | re.IGNORECASE)

    at_matcher = re.compile(r"@|\sat\s", re.IGNORECASE)
    dot_matcher = re.compile(r"\.|\sdot\s", re.IGNORECASE)

    def iter_filth(self, text: str, document_name: Optional[str] = None) -> Generator[Filth, None, None]:
        """Yields discovered filth in the provided ``text``.

        :param text: The dirty text to clean.
        :type text: str
        :param document_name: The name of the document to clean.
        :type document_name: str, optional
        :return: An iterator to the discovered :class:`Filth`
        :rtype: Iterator[:class:`Filth`]
        """

        if re.search(self.at_matcher, text) and re.search(self.dot_matcher, text):
            yield from super().iter_filth(text=text, document_name=document_name)
