import phonenumbers

from typing import Optional

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
    name = 'phone'

    def __init__(self, region: str = 'US', **kwargs):
        super(PhoneDetector, self).__init__(**kwargs)
        self.region = region

    def iter_filth(self, text, document_name: Optional[str] = None):
        # create a copy of text to handle multiple phone numbers correctly
        for match in phonenumbers.PhoneNumberMatcher(text, self.region):
            yield PhoneFilth(
                beg=match.start,
                end=match.end,
                text=match.raw_string,
                detector_name=self.name,
                document_name=document_name
            )
