"""
This modules provides a detector for date of births.

It is simply looking for any detected dates that are more than 18 years and date of birth has been
mentioned within 2 previous lines.

Using 18+ years may not be suitable for all use cases; use with caution.
"""

import re
from dateparser.search import search_dates
from datetime import datetime

from typing import Optional, Iterable

from . import register_detector
from .base import Detector
from ..filth.date_of_birth import DoBFilth


class DoBDetector(Detector):
    filth_cls = DoBFilth
    name = 'dob'

    def __init__(self, context_before: Optional[int] = None, context_after: Optional[int] = None,
                 min_age_years: Optional[int] = None, trigger_words: Optional[Iterable[str]] = None,
                 **kwargs):
        super(DoBDetector, self).__init__(**kwargs)
        if context_before is None:
            self.context_before = int(2)
        if context_after is None:
            self.context_after = int(1)
        if min_age_years is None:
            self.min_age_years = int(18)
        if trigger_words is None:
            self.trigger_words = ['birth', 'dob', 'd.o.b.']

        # only using lowercase matches
        self.trigger_words = [word.lower() for word in trigger_words]

    def iter_filth(self, text, document_name: Optional[str] = None):
        # splitting lines using linebreaks, which is then used for counting
        lines = text.split('\n')

        for count, line in enumerate(lines):
            # using the dateparser lib - locale can be set here
            date_picker = search_dates(line, languages=['en'])
            if date_picker is not None:
                for identified_date in date_picker:
                    # calculate if at least 18 years has lapsed
                    # find if anything related to date of birth has been mentioned in the previous lines
                    if datetime.now().year - identified_date[1].year >= self.min_age_years and \
                            any(trigger_word in ' '.join(lines[count - self.context_before:count + self.context_after]
                                                         ).lower() for trigger_word in self.trigger_words):
                        # date_picker doesn't return the startend, so using re.finditer for the start & end locations
                        found_dates = re.finditer(re.escape(r"{0}".format(identified_date[0])), text)
                        # Iterate over each found string matching this regex and yield some filth
                        for instance in found_dates:
                            yield self.filth_cls(
                                beg=instance.start(),
                                end=instance.end(),
                                text=instance.group(),
                                detector_name=self.name,
                                document_name=document_name,
                            )


register_detector(DoBDetector, autoload=False)
