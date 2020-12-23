"""
This modules provides a detector for date of births.

The filter_type = contextual is simply looking for any detected dates that are more than 18 years
and date of birth has been mentioned within 2 previous lines.

Another option is to nuke all date of birth that is between 18 and 100 years.

Using 18+ years may not be suitable for all use cases; use with caution.
"""
import re
from dateparser.search import search_dates
from datetime import datetime

from typing import Optional


from scrubadub.detectors.base import Detector
from scrubadub.filth import DoBFilth


class DoBDetector(Detector):
    filth_cls = DoBFilth
    name = 'dob'

    def __init__(self, context_before: Optional[int] = None, context_after: Optional[int] = None,
                 min_age_years: Optional[int] = None, max_age_years: Optional[int] = None,
                 filter_type: Optional[str] = None,
                 **kwargs):

        if context_before is None:
            self.context_before = int(2)
        if context_after is None:
            self.context_after = int(1)
        if min_age_years is None:
            self.min_age_years = int(18)
        if max_age_years is None:
            self.max_age_years = int(100)
        if filter_type is None:
            self.filter_type = 'contextual'

        self.trigger_words = ['birth', 'born', 'dob', 'd.o.b.']
        super(DoBDetector, self).__init__(**kwargs)

    def iter_filth(self, text: str, document_name: Optional[str] = None):
        """ filter_type:
            contextual = only look for dates that are in close proximity with the words similar to birth
            nuke = remove everything beyond x number of years, default x = self.min_age_years = 18

        :param text: the text from the blobstring
        :param document_name: optional
        :return:
        """
        lines = text.split('\n')

        for count, line in enumerate(lines):
            # using the dateparser lib - locale can be set here
            language, region = self.locale_split(self.locale)
            date_picker = search_dates(line, languages=[language])
            if date_picker is not None:
                for identified_date in date_picker:
                    # calculate if at least 18 years has lapsed
                    # find if anything related to date of birth has been mentioned in the previous lines
                    # if the captured str does not start with a phone number type plus sign
                    if not str(identified_date[0]).startswith('+') and \
                            self.min_age_years <= datetime.now().year - identified_date[1].year <= self.max_age_years:
                        if self.filter_type == 'contextual':
                            found_dates = re.finditer(re.escape(r"{0}".format(identified_date[0])), text)
                        elif self.filter_type == 'nuke':
                            if any(trigger_word in ' '.join(lines[count - self.context_before:count + self.context_after
                                                                  ]).lower() for trigger_word in self.trigger_words):
                                # date_picker doesn't return the start end, so using re.finditer
                                found_dates = re.finditer(re.escape(r"{0}".format(identified_date[0])), text)
                        for instance in found_dates:
                            yield self.filth_cls(
                                beg=instance.start(),
                                end=instance.end(),
                                text=instance.group(),
                                detector_name=self.name,
                                document_name=document_name,
                                locale=self.locale,
                            )

    @classmethod
    def supported_locale(cls, locale: str) -> bool:
        """Returns true if this ``Detector`` supports the given locale.

        :param locale: The locale of the documents in the format: 2 letter lower-case language code eg "en", "es".
        :type locale: str
        :return: ``True`` if the locale is supported, otherwise ``False``
        :rtype: bool
        """
        language, region = cls.locale_split(locale)
        return language in ['en']
    
