import re
import pathlib
from typing import Dict, Optional

import nltk
import pyap.source_US.data

from . import register_detector
from .sklearn import BIOTokenSklearnDetector
from ..filth import AddressFilth


class AddressTokeniser(nltk.tokenize.destructive.NLTKWordTokenizer):
    PUNCTUATION = [
        (re.compile(r'([^\.])(\.)([\]\)}>"\'' u"»”’ " r"]*)[\t\r\f\v]*$", re.U), r"\1 \2 \3 "),
        (re.compile(r"([:,])([^\d])"), r" \1 \2"),
        (re.compile(r"([:,])$"), r" \1 "),
        (re.compile(r"([:\n])"), r" \1 "),
        (re.compile(r"\.{2,}", re.U), r" \g<0> "),  # See https://github.com/nltk/nltk/pull/2322
        (re.compile(r"[;@#$%&]"), r" \g<0> "),
        (
            re.compile(r'([^\.])(\.)([\]\)}>"\']*)[\t\r\f\v]*$'),
            r"\1 \2\3 ",
        ),  # Handles the final period.
        # Earlier we put a space before the full-stop, if there is something in the format X.X.X .
        # transform this back to X.X.X.
        (re.compile(r'(?<!\w)(\w(?:\.\w)+) +(\.)'), r'\1\2'),
        # Remove special whitespace by replacing anything that's not (^) not whitespace (\S) and that's not a newline
        # This is the same as removing whitespace (\s) except newlines (\n)
        (re.compile(r"[^\S\n]+"), " "),
        (re.compile(r"[?!]"), r" \g<0> "),
        (re.compile(r"([^'])' "), r"\1 ' "),
        (re.compile(r"[*]", re.U), r" \g<0> "),  # See https://github.com/nltk/nltk/pull/2322
    ]

    def tokenize(self, text, convert_parentheses=False, return_str=False):
        for regexp, substitution in self.STARTING_QUOTES:
            text = regexp.sub(substitution, text)

        for regexp, substitution in self.PUNCTUATION:
            text = regexp.sub(substitution, text)

        # Handles parentheses.
        regexp, substitution = self.PARENS_BRACKETS
        text = regexp.sub(substitution, text)
        # Optionally convert parentheses
        if convert_parentheses:
            for regexp, substitution in self.CONVERT_PARENTHESES:
                text = regexp.sub(substitution, text)

        # Handles double dash.
        regexp, substitution = self.DOUBLE_DASHES
        text = regexp.sub(substitution, text)

        # add extra space to make things easier
        text = " " + text + " "

        for regexp, substitution in self.ENDING_QUOTES:
            text = regexp.sub(substitution, text)

        for regexp in self.CONTRACTIONS2:
            text = regexp.sub(r" \1 \2 ", text)
        for regexp in self.CONTRACTIONS3:
            text = regexp.sub(r" \1 \2 ", text)

        return text if return_str else [x for x in text.split() if x != '']


class SklearnAddressDetector(BIOTokenSklearnDetector):
    name = "sklearn_address"
    label_filth_map = {
        'ADD': AddressFilth,
        'ADDRESS': AddressFilth,
        'I-ADD': AddressFilth,
        'B-ADD': AddressFilth,
        'I-ADDRESS': AddressFilth,
        'B-ADDRESS': AddressFilth,
    }

    # models / sklearn_address

    BUILDING_WORDS = [
        'flat', 'building', 'bldg', 'bld', 'apartment', 'apt', 'house', 'studio', 'suite', 'room'
    ]

    DIRECTION_WORDS = [
        'north', 'south', 'east', 'west', 'northern', 'southern', 'eastern', 'western',
    ]

    STREET_WORDS = [x.lower() for x in pyap.source_US.data.street_type_list]

    # TODO: Include these prefixes/suffixes
    # https://en.wikipedia.org/wiki/List_of_generic_forms_in_place_names_in_Ireland_and_the_United_Kingdom
    PLACE_SUFFIXES = [
        'town', 'ton', 'land', 'lands', 'ville', 'berg', 'burgh', 'brough', 'borough', 'bury', 'view', 'port',
        'stad', 'stead', 'furt', 'chester', 'mouth', 'fort', 'haven', 'side', 'shire', 'city', 'by',
        'cester', 'ford', 'ham', 'worth', 'berry'
    ]

    PLACE_PREFIXES = [
        # Include rivers here
        'thames', 'severn', 'trent', 'wye', 'ouse', 'tyne', 'mersey', 'avon', 'aber',
    ]

    COUNTRY_WORDS = [
        'united', 'kingdom', 'britain', 'england', 'ni', 'uk', 'gb', 'gbr', 'scotland', 'ireland', 'wales',
        'cymry', 'cymru', 'alba'
    ]

    # Added as dates looked similar to addresses
    DATE_WORDS = [
        'january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november',
        'december', 'jan', 'feb', 'mar', 'apr', 'jun', 'jul', 'aug', 'sep', 'sept', 'oct', 'nov', 'dec',
        'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday',
        'mon', 'tue', 'wed', 'weds', 'thurs', 'fri', 'sat', 'sun',
    ]

    def __init__(self, model_path_prefix: Optional[str] = None, b_token_required: bool = True, **kwargs):

        if model_path_prefix is None:
            model_path_prefix = str(pathlib.Path(__file__).parent / 'models' / 'sklearn_address')

        super(SklearnAddressDetector, self).__init__(
            model_path_prefix=model_path_prefix, b_token_required=b_token_required, **kwargs
        )
        self.tokeniser = AddressTokeniser()

    @staticmethod
    def create_features_single_token(token: str, prefix: str = '') -> Dict:
        token = token.strip(' \t\r\v\f')
        address_punctuation = token.lower() in ('\n', '.', ',')
        street_word = token.lower() in SklearnAddressDetector.STREET_WORDS
        building_word = token.lower() in SklearnAddressDetector.BUILDING_WORDS
        direction_word = token.lower() in SklearnAddressDetector.DIRECTION_WORDS
        place_prefix = sum(token.startswith(prefix) for prefix in SklearnAddressDetector.PLACE_PREFIXES)
        place_suffix = sum(token.endswith(suffix) for suffix in SklearnAddressDetector.PLACE_SUFFIXES)
        country_word = token.lower() in SklearnAddressDetector.COUNTRY_WORDS
        date_word = token.lower() in SklearnAddressDetector.DATE_WORDS

        features = {
            prefix + 'capitalised': token.istitle(),
            prefix + 'lower': token.islower(),
            prefix + 'upper': token.isupper(),
            prefix + 'numeric': token.isdigit(),
            prefix + 'alphanumeric': any(c.isdigit() for c in token) and any(c.isalpha() for c in token),
            prefix + 'address_punctuation': address_punctuation,
            prefix + 'building_word': building_word,
            prefix + 'direction_word': direction_word,
            prefix + 'street_word': street_word,
            prefix + 'place_prefix': place_prefix,
            prefix + 'place_suffix': place_suffix,
            prefix + 'country_word': country_word,
            prefix + 'date_word': date_word,
            # prefix + 'length': len(token),
            prefix + 'length_short': len(token) <= 4,
            prefix + 'length_long': len(token) > 20,
        }
        return features

    @classmethod
    def supported_locale(cls, locale: str) -> bool:
        """Returns true if this ``Detector`` supports the given locale.

        :param locale: The locale of the documents in the format: 2 letter lower-case language code followed by an
                       underscore and the two letter upper-case country code, eg "en_GB" or "de_CH".
        :type locale: str
        :return: ``True`` if the locale is supported, otherwise ``False``
        :rtype: bool
        """
        language, region = cls.locale_split(locale)
        return region in ['GB']


register_detector(SklearnAddressDetector, autoload=False)
