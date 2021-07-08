
from typing import Generator, Optional, Sequence, List, Iterable

try:
    import spacy
    from spacy.language import Language
    from spacy.tokens import Doc
    from spacy.tokens import Span
except ImportError as e:
    if e.name == "spacy":
        raise ImportError(
            "Could not find module 'spacy'. If you want to use extras,"
            " make sure you install scrubadub with 'pip install scrubadub[spacy]'"
        )

from . import register_detector
from ..filth import Filth
from .spacy import SpacyEntityDetector


@Language.component("expand_person_entities")
def expand_person_entities(doc: spacy.tokens.doc.Doc) -> spacy.tokens.doc.Doc:
    """ Expand person entity by person title.

    This is the spacy method for adding a label on top of the normal named entity labels.
    This method preserves the existing labels as well as creating a new label for expanded person entities.
    The expanded person entities can be retrieved by using the list doc._.person_titles.
    Each item in the list doc._.person_titles is a spacy.tokens.span.Span,
    which contains the start and end locations.

    :return: spacy doc object
    """
    if doc._.person_titles is None:
        doc._.person_titles = []

    if (doc.lang_ not in SpacyNameDetector.NAME_PREFIXES and doc.lang_ not in SpacyNameDetector.NAME_PREFIXES) or \
            doc.lang_ not in SpacyNameDetector.NOUN_TAGS:
        raise NotImplementedError(f"Language {doc.lang_} is not supported by SpacyNameTitleDetector")

    noun_tags = SpacyNameDetector.NOUN_TAGS[doc.lang_]

    for token in doc:
        # if the token is a prefix
        prefix_tag = 0
        suffix_tag = 0
        span_obj = []  # type: List[int]
        tokens_ids_in_sentence = [span_token.i for span_token in token.sent]
        text = token.text
        if text == ':':
            text = doc[token.i - 1].text + ':'

        if doc.lang_ in SpacyNameDetector.NAME_PREFIXES and \
                text.lower() in SpacyNameDetector.NAME_PREFIXES[doc.lang_]:
            span_obj = [
                span_token.i
                for span_token in doc[token.i:token.i + SpacyNameDetector.TOKEN_SEARCH_DISTANCE + 1]
                if (span_token.dep_ != "punct" and span_token.tag_ in noun_tags and
                    not span_token.is_stop and span_token.i in tokens_ids_in_sentence)
            ]
            prefix_tag = 1
            if doc.lang_ in SpacyNameDetector.NAME_SUFFIXES and len(span_obj) > 1 and \
                    str(doc[span_obj[-1]]).lower() in SpacyNameDetector.NAME_SUFFIXES[doc.lang_]:
                suffix_tag = 1

        if doc.lang_ in SpacyNameDetector.NAME_SUFFIXES and \
                text.lower() in SpacyNameDetector.NAME_SUFFIXES[doc.lang_]:
            span_obj = [
                span_token.i
                for span_token in doc[token.i - SpacyNameDetector.TOKEN_SEARCH_DISTANCE:token.i + 1]
                if (span_token.dep_ != "punct" and span_token.tag_ in noun_tags and
                    not span_token.is_stop and span_token.i in tokens_ids_in_sentence)
            ]
            suffix_tag = 1
            if str(doc[span_obj[0]]).lower() in SpacyNameDetector.NAME_PREFIXES[doc.lang_]:
                prefix_tag = 1

        if len(span_obj) >= SpacyNameDetector.MINIMUM_NAME_LENGTH:
            # create slice with spacy span to include new entity
            entity = Span(doc, min(span_obj), max(span_obj) + 1, label="PERSON")
            entity2 = Span(doc, min(span_obj) + prefix_tag, max(span_obj) + 1 - suffix_tag, label="PERSON")
            # update spacy ents to include the new entity
            if entity not in doc._.person_titles:
                doc._.person_titles.append(entity)
            if len(entity2) > 0 and entity2 not in doc._.person_titles:
                doc._.person_titles.append(entity2)
    return doc


class SpacyNameDetector(SpacyEntityDetector):
    """Add an extension to the spacy detector to look for tokens that often occur before or after names of people's
    names, a prefix might be Hello as in "Hello Jane", or Mrs as in "Mrs Jane Smith" and a suffix could be PhD as
    in "Jane Smith PhD".

    See the ``SpacyDetector`` for further info on how to use this detector as it shares many similar options.

    Currently only english prefixes and sufixes are supported, but other language titles can be easily added, as in
    the example below:

    >>> import scrubadub, scrubadub.detectors.spacy_name_title
    >>> scrubadub.detectors.spacy_name_title.SpacyNameDetector.NOUN_TAGS['de'] = ['NN', 'NE', 'NNE']
    >>> scrubadub.detectors.spacy_name_title.SpacyNameDetector.NAME_PREFIXES['de'] = ['frau', 'herr']
    >>> detector = scrubadub.detectors.spacy_name_title.SpacyNameDetector(locale='de_DE', model='de_core_news_sm')
    >>> scrubber = scrubadub.Scrubber(detector_list=[detector], locale='de_DE')
    >>> scrubber.clean("bleib dort Frau Schmidt")
    'bleib dort {{NAME+NAME}}'
    """
    name = "spacy_name"

    NAME_PREFIXES = {
        "en": [
            # Titles
            'mr', 'mr.', 'mister', 'mrs', 'mrs.', 'misses', 'ms', 'ms.', 'miss', 'dr', 'dr.', 'doctor', 'prof',
            'prof.', 'professor', 'lord', 'lady', 'rev', 'rev.', 'reverend', 'hon', 'hon.', 'honourable', 'hhj',
            'honorable', 'judge', 'sir', 'madam',
            # Greetings
            'hello', 'dear', 'hi', 'hey', 'from', 'regards',
            # emails
            'to:', 'from:', 'sender:',
        ],
    }

    NAME_SUFFIXES = {
        "en": ['phd', 'bsc', 'msci', 'ba', 'md', 'qc', 'ma', 'mba'],
    }

    NOUN_TAGS = {
        'en': ["NNP", "NN", "NNPS"],
    }

    # This is the number of tokens to look for a name after the title
    TOKEN_SEARCH_DISTANCE = 3

    # This is the minimum number of tokens that is considered a name
    MINIMUM_NAME_LENGTH = 1

    def __init__(self, include_spacy: bool = True, **kwargs):
        """Initialise the ``Detector``.

        :param include_spacy: include default spacy library in addition to title detector.
        :type include_spacy: bool, default, False
        :param named_entities: Limit the named entities to those in this list, defaults to ``{'PERSON', 'PER', 'ORG'}``.
        :type named_entities: Iterable[str], optional
        :param model: The name of the spacy model to use, it must contain a 'ner' step in the model pipeline (most
            do, but not all).
        :type model: str, optional
        :param name: Overrides the default name of the :class:``Detector``
        :type name: str, optional
        :param locale: The locale of the documents in the format: 2 letter lower-case language code followed by an
                       underscore and the two letter upper-case country code, eg "en_GB" or "de_CH".
        :type locale: str, optional
        """
        Doc.set_extension('person_titles', default=None, force=True)
        super(SpacyNameDetector, self).__init__(**kwargs)

        # Add the expand person title component after the named entity recognizer
        self.nlp.add_pipe('expand_person_entities', after='ner')
        self.include_spacy = include_spacy

    @staticmethod
    def _get_affix_entities(doc: spacy.tokens.doc.Doc) -> Iterable[spacy.tokens.span.Span]:
        return doc._.person_titles

    @staticmethod
    def _get_affix_and_spacy_entities(doc: spacy.tokens.doc.Doc) -> Iterable[spacy.tokens.span.Span]:
        return (doc.ents + doc._.person_titles)

    def iter_filth_documents(self, document_list: Sequence[str],
                             document_names: Sequence[Optional[str]]) -> Generator[Filth, None, None]:
        """Yields discovered filth in a list of documents.

        :param document_list: A list of documents to clean.
        :type document_list: List[str]
        :param document_names: A list containing the name of each document.
        :type document_names: List[str]
        :return: A list containing all the spacy doc
        :rtype: Sequence[Optional[str]]
        """

        if self.include_spacy:
            entity_function = self._get_affix_and_spacy_entities
        else:
            entity_function = self._get_affix_entities

        yield from self._yield_filth(document_list, document_names, get_entity_function=entity_function)

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
        return (
            (language in SpacyNameDetector.NAME_PREFIXES or language in SpacyNameDetector.NAME_SUFFIXES) and
            language in SpacyNameDetector.NOUN_TAGS
        )


register_detector(SpacyNameDetector, autoload=False)

__all__ = ['SpacyNameDetector']
