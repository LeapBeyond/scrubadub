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
        (re.compile(r'([^\.]{2,})(\.)([\]\)}>"\'' u"»”’ " r"]*)[\t\r\f\v]*$", re.U), r"\1 \2 \3 "),
        (re.compile(r"([:,])([^\d])"), r" \1 \2"),
        (re.compile(r"([:,])$"), r" \1 "),
        (re.compile(r"([:\n])"), r" \1 "),
        (re.compile(r"\.{2,}", re.U), r" \g<0> "),  # See https://github.com/nltk/nltk/pull/2322
        (re.compile(r"[;@#$%&]"), r" \g<0> "),
        (
            re.compile(r'([^\.]{2,})(\.)([\]\)}>"\']*)[\t\r\f\v]*$'),
            r"\1 \2\3 ",
        ),  # Handles the final period.
        # Earlier we put a space before the full-stop, if there is something in the format X.X.X .
        # transform this back to X.X.X.
        # (re.compile(r'(?<!\w)(\w(?:\.\w)+) +(\.)'), r'\1\2'),
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

        # Only splitting by spaces to get newlines as tokens
        return text if return_str else [x for x in text.split(' ') if x != '']


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
        'flat', 'flats', 'building', 'buildings', 'bldg', 'bld', 'apartment', 'apartments', 'apt', 'house', 'houses',
        'studio', 'studios', 'suite', 'suites', 'room', 'rooms', 'centre', 'penthouse', 'residence', 'office', 'tower',
        'court',
    ]

    PO_BOX_WORDS = [
        'po', 'box', 'p.o', 'p.o.'
    ]

    DIRECTION_WORDS = [
        'north', 'south', 'east', 'west', 'northern', 'southern', 'eastern', 'western',
    ]

    STREET_WORDS = [x.lower() for x in pyap.source_US.data.street_type_list]

    # TODO: Include these prefixes/suffixes
    # https://en.wikipedia.org/wiki/List_of_generic_forms_in_place_names_in_Ireland_and_the_United_Kingdom
    PLACE_WORDS = {
        'town', 'ton', 'land', 'lands', 'ville', 'berg', 'burgh', 'brough', 'borough', 'bury', 'view', 'port',
        'stad', 'stead', 'furt', 'chester', 'mouth', 'fort', 'haven', 'side', 'shire', 'city', 'cum',
        'cester', 'ford', 'ham', 'worth', 'berry', 'field', 'church,'
        # Include rivers here
        'thames', 'severn', 'trent', 'wye', 'ouse', 'tyne', 'mersey', 'avon', 'aber',
        'upon'
    }
    # TODO: add towns
    # TODO: PO Box address
    # TODO: the word address

    COUNTY_WORDS = {
        'bedfordshire', 'buckinghamshire', 'cambridgeshire', 'cheshire', 'cleveland', 'cornwall', 'cumbria',
        'derbyshire', 'devon', 'dorset', 'durham', 'sussex', 'essex', 'gloucestershire', 'greater', 'london',
        'manchester', 'hampshire', 'hertfordshire', 'kent', 'lancashire', 'leicestershire', 'lincolnshire',
        'merseyside', 'norfolk', 'yorkshire', 'northamptonshire', 'northumberland', 'nottinghamshire', 'oxfordshire',
        'shropshire', 'somerset', 'staffordshire', 'suffolk', 'surrey', 'tyne', 'wear', 'warwickshire',
        'berkshire', 'midlands', 'sussex', 'wiltshire', 'worcestershire', 'flintshire', 'glamorgan', 'merionethshire',
        'monmouthshire', 'montgomeryshire', 'pembrokeshire', 'radnorshire', 'anglesey', 'breconshire',
        'caernarvonshire', 'cardiganshire', 'carmarthenshire', 'denbighshire', 'aberdeen', 'aberdeenshire', 'angus',
        'argyll', 'bute', 'edinburgh', 'clackmannanshire', 'dumfries', 'galloway', 'dundee', 'ayrshire',
        'dunbartonshire', 'lothian', 'renfrewshire', 'eilean', 'siar', 'falkirk', 'fife', 'glasgow', 'highland',
        'inverclyde', 'midlothian', 'moray', 'ayrshire', 'lanarkshire', 'orkney', 'perth', 'kinross', 'renfrewshire',
        'borders', 'shetland', 'ayrshire', 'lanarkshire', 'stirling', 'dunbartonshire', 'lothian', 'antrim', 'armagh',
        'fermanagh', 'derry', 'londonderry', 'tyrone'
    }

    COUNTRY_WORDS = {
        'united', 'kingdom', 'britain', 'england', 'ni', 'uk', 'gb', 'gbr', 'scotland', 'ireland', 'wales',
        'cymry', 'cymru', 'alba'
    }

    # Added as dates looked similar to addresses
    DATE_WORDS = [
        'january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november',
        'december', 'jan', 'feb', 'mar', 'apr', 'jun', 'jul', 'aug', 'sep', 'sept', 'oct', 'nov', 'dec',
        'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday',
        'mon', 'tue', 'wed', 'weds', 'thurs', 'fri', 'sat', 'sun',
    ]

    # Regexs allow for 5 <-> S errors in OCR
    POSTCODE_START = re.compile(r"""
        (?:[Ww][Cc][0-9sS][abehmnprvwxyABEHMNPRVWXY])|
        (?:[Ee][Cc][1-4][abehmnprvwxyABEHMNPRVWXY])|
        (?:[Nn][Ww]1[Ww])|
        (?:[Ss][Ee]1[Pp])|
        (?:[Ss][Ww]1[abehmnprvwxyABEHMNPRVWXY])|
        (?:[EeNnWw]1[a-hjkpstuwA-HJKPSTUW5])|
        (?:[BbEeGgLlMmNnSsWw][0-9sS][0-9sS]?)|
        (?:[a-pr-uwyzA-PR-UWYZ5][a-hk-yxA-HK-XY5][0-9sS][0-9sS]?)
    """, re.VERBOSE)

    POSTCODE_END = re.compile(r"""[0-9sS][abd-hjlnp-uw-zABD-HJLNP-UW-Z5]{2}""", re.VERBOSE)

    def __init__(self, model_path_prefix: Optional[str] = None, b_token_required: bool = False,
                 minimum_ntokens: int = 4, number_missing_tokens_allowed: Optional[int] = 3,
                 number_missing_characters_allowed: Optional[int] = None, **kwargs):

        if model_path_prefix is None:
            model_path_prefix = str(pathlib.Path(__file__).parent / 'models' / 'sklearn_address')

        super(SklearnAddressDetector, self).__init__(
            model_path_prefix=model_path_prefix, b_token_required=b_token_required, minimum_ntokens=minimum_ntokens,
            number_missing_tokens_allowed=number_missing_tokens_allowed,
            number_missing_characters_allowed=number_missing_characters_allowed, **kwargs
        )
        self.tokeniser = AddressTokeniser()

    @staticmethod
    def create_features_single_token(token: str, prefix: str = '') -> Dict:
        token = token.strip(' \t\r\v\f')
        address_punctuation = any(punct in token.lower() for punct in ('\n', ','))
        street_word = token.lower() in SklearnAddressDetector.STREET_WORDS
        building_word = token.lower() in SklearnAddressDetector.BUILDING_WORDS
        direction_word = token.lower() in SklearnAddressDetector.DIRECTION_WORDS
        place_word = sum(word in token.lower() for word in SklearnAddressDetector.PLACE_WORDS)
        county_word = token.lower() in SklearnAddressDetector.COUNTY_WORDS
        country_word = token.lower() in SklearnAddressDetector.COUNTRY_WORDS
        date_word = token.lower() in SklearnAddressDetector.DATE_WORDS
        po_box_word = token.lower() in SklearnAddressDetector.PO_BOX_WORDS
        postcode_start = re.match(SklearnAddressDetector.POSTCODE_START, token) is not None
        postcode_end = re.match(SklearnAddressDetector.POSTCODE_END, token) is not None

        features = {
            prefix + 'capitalised': token.istitle(),
            prefix + 'lower': token.islower(),
            prefix + 'upper': token.isupper(),
            prefix + 'numeric': any(c.isdigit() for c in token),
            prefix + 'alphanumeric': any(c.isdigit() for c in token) and any(c.isalpha() for c in token),
            prefix + 'address_punctuation': address_punctuation,
            prefix + 'building_word': building_word,
            prefix + 'direction_word': direction_word,
            prefix + 'street_word': street_word,
            prefix + 'place_word': place_word,
            prefix + 'po_box_word': po_box_word,
            prefix + 'county_word': county_word,
            prefix + 'country_word': country_word,
            prefix + 'date_word': date_word,
            # Limit to 5 to prevent ML from learning fingerprint of common addresses
            prefix + 'length': len(token) if len(token) <= 5 else 5,
            prefix + 'length_short': len(token) <= 4,
            prefix + 'length_long': len(token) > 20,
            prefix + 'postcode_start': postcode_start,
            prefix + 'postcode_end': postcode_end,
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
