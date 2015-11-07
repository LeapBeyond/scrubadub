import phonenumbers

from .base import Detector
from ..filth import PhoneFilth


class PhoneDetector(Detector):
    """Remove phone numbers from dirty dirty ``text`` using
    `python-phonenumbers
    <https://github.com/daviddrysdale/python-phonenumbers>`_, a port of a
    Google project to correctly format phone numbers in text.

    ``region`` specifies the best guess region to start with (default:
    ``"US"``). Specify ``None`` to only consider numbers with a leading
    ``+`` to be considered.
    """
    filth_cls = PhoneFilth
    region = 'US'

    def iter_filth(self, text):
        # create a copy of text to handle multiple phone numbers correctly
        for match in phonenumbers.PhoneNumberMatcher(text, self.region):
            yield PhoneFilth(
                beg=match.start,
                end=match.end,
                text=match.raw_string,
            )
