"""
This modules provides a detector for date of births.

The filter_type = contextual is simply looking for any detected dates that are more than 18 years
and date of birth has been mentioned within 2 previous lines.

Another option is to nuke all date of birth that is between 18 and 100 years.

Using 18+ years may not be suitable for all use cases; use with caution.
"""
import re
import logging
from dateparser.search import search_dates
from datetime import datetime

from typing import Optional, List, Generator

from scrubadub.detectors.catalogue import register_detector
from .base import Detector
from ..filth.base import Filth
from ..filth.date_of_birth import DateOfBirthFilth


@register_detector
class DateOfBirthDetector(Detector):
    """This detector aims to detect dates of birth in text.

    First all possible dates are found, then they are filtered to those that would result in people being between
    ``DateOfBirthFilth.min_age_years`` and ``DateOfBirthFilth.max_age_years``, which default to 18 and 100
    respectively.

    If ``require_context`` is True, we search for one of the possible ``context_words`` near the found date. We search
    up to ``context_before`` lines before the date and up to ``context_after`` lines after the date. The context that
    we search for are terms like `'birth'` or `'DoB'` to increase the likelihood that the date is indeed a date of
    birth. The context words can be set using the ``context_words`` parameter, which expects a list of strings.

    >>> import scrubadub, scrubadub.detectors.date_of_birth
    >>> DateOfBirthFilth.min_age_years = 12
    >>> scrubber = scrubadub.Scrubber(detector_list=[
    ...     scrubadub.detectors.date_of_birth.DateOfBirthDetector(),
    ... ])
    >>> scrubber.clean("I was born on 10-Nov-2008.")
    'I was born {{DATE_OF_BIRTH}}.'

    """
    name = 'date_of_birth'
    filth_cls = DateOfBirthFilth
    autoload = False

    context_words_language_map = {
        'en': ['birth', 'born', 'dob', 'd.o.b.'],
        'de': ['geburt', 'geboren', 'geb', 'geb.'],
    }

    def __init__(self, context_before: int = 2, context_after: int = 1, require_context: bool = True,
                 context_words: Optional[List[str]] = None, **kwargs):
        """Initialise the detector.

        :param context_before: The number of lines of context to search before the date
        :type context_before: int
        :param context_after: The number of lines of context to search after the date
        :type context_after: int
        :param require_context: Set to False if your dates of birth are not near words that provide context (such as
            "birth" or "DOB").
        :type require_context: bool
        :param context_words: A list of words that provide context related to dates of birth, such as the following:
            'birth', 'born', 'dob' or 'd.o.b.'.
        :type context_words: bool
        :param name: Overrides the default name of the :class:``Detector``
        :type name: str, optional
        :param locale: The locale of the documents in the format: 2 letter lower-case language code followed by an
                       underscore and the two letter upper-case country code, eg "en_GB" or "de_CH".
        :type locale: str, optional
        """
        super(DateOfBirthDetector, self).__init__(**kwargs)

        self.context_before = context_before
        self.context_after = context_after
        self.require_context = require_context

        try:
            self.context_words = self.context_words_language_map[self.language]
        except KeyError:
            raise ValueError("DateOfBirthDetector does not support language {}.".format(self.language))

        if context_words is not None:
            self.context_words = context_words

        self.context_words = [word.lower() for word in self.context_words]

    def iter_filth(self, text: str, document_name: Optional[str] = None) -> Generator[Filth, None, None]:
        """Search ``text`` for ``Filth`` and return a generator of ``Filth`` objects.

        :param text: The dirty text that this Detector should search
        :type text: str
        :param document_name: Name of the document this is being passed to this detector
        :type document_name: Optional[str]
        :return: The found Filth in the text
        :rtype: Generator[Filth]
        """

        # using the dateparser lib - locale can be set here
        try:
            date_picker = search_dates(text, languages=[self.language])
        except RecursionError:
            logger = logging.getLogger("scrubadub.detectors.date_of_birth.DateOfBirthDetector")
            logger.error(f"The document '{document_name}' caused a recursion error in dateparser.")
            raise
        if date_picker is None:
            return None

        lines = text.split('\n')

        for identified_string, identified_date in date_picker:
            # Skip anything that could be a phone number, dates rarely begin with a plus
            suspected_phone_number = str(identified_string).startswith('+')
            if suspected_phone_number:
                continue

            # Skip any dates that fall outside of the configured age range
            years_since_identified_date = datetime.now().year - identified_date.year
            within_age_range = (DateOfBirthFilth.min_age_years <= years_since_identified_date <=
                                DateOfBirthFilth.max_age_years)
            if not within_age_range:
                continue

            # If its desired, search for context, if no context is found skip this identified date
            if self.require_context:
                found_context = False
                # Search line by line for the identified date string (identified_string)
                for i_line, line in enumerate(lines):
                    if identified_string not in line:
                        continue
                    # when you find the identified_string, search for context
                    from_line = max(i_line - self.context_before, 0)
                    to_line = max(i_line + self.context_after + 1, 0)
                    text_context = ' '.join(lines[from_line:to_line]).lower()
                    found_context = any(context_word in text_context for context_word in self.context_words)
                    # If you find any context around any instances of this string, all instance are PII
                    if found_context:
                        break
                # If we didn't find any context, this isnt PII, so skip this date
                if not found_context:
                    continue

            found_dates = re.finditer(re.escape(identified_string), text)

            for instance in found_dates:
                yield DateOfBirthFilth(
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
        return language in cls.context_words_language_map.keys()


__all__ = ['DateOfBirthDetector']
