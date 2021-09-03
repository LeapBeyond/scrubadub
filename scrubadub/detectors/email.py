import re

from scrubadub.detectors.catalogue import register_detector
from .base import RegexDetector
from ..filth import EmailFilth


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
        r"[a-z0-9!#$%&'*+\/=?^_`{|}~-]+"           # start with this character
        r"(?:\.[a-z0-9!#$%&'*+\/=?^_`{|}~-]+)*"    # valid next characters
        r"(@|\sat\s)"                              # @ or at fanciness
        r"(?:"
        r"[a-z0-9]"                                # domain starts like this
        r"(?:[a-z0-9-]*[a-z0-9])?"                 # might have this
        r"(\.|\sdot\s)"                            # . or dot fanciness
        r")+"                                      # repeat as necessary
        r"[a-z0-9](?:[a-z0-9-]*[a-z0-9])?"         # end of domain
    ), re.VERBOSE | re.IGNORECASE)


    # def iter_filth(self, text: str, document_name: Optional[str] = None) -> Generator[Filth, None, None]:
    #     """Yields discovered filth in the provided ``text``.
    #
    #     :param text: The dirty text to clean.
    #     :type text: str
    #     :param document_name: The name of the document to clean.
    #     :type document_name: str, optional
    #     :return: An iterator to the discovered :class:`Filth`
    #     :rtype: Iterator[:class:`Filth`]
    #     """
    #
    #     if re.match(self.at_matcher, text) and re.match(self.dot_matcher, text):
    #         yield from super().iter_filth(text=text, document_name=document_name)
