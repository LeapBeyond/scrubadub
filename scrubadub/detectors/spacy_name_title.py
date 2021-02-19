import copy

from typing import Generator, Optional, Sequence

try:
    import spacy
    # new in spacy v3
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

    if doc.lang_ not in SpacyNameTitleDetector.NAME_TITLES:
        raise NotImplementedError(f"Language {doc.lang_} is not supported by SpacyNameTitleDetector")

    for token in doc:
        # if the token is a title
        if token.text.lower() in SpacyNameTitleDetector.NAME_TITLES[doc.lang_]:
            # span of title plus n tokens to inspect
            span_obj = [
                span_token.i
                for span_token in doc[token.i:token.i + SpacyNameTitleDetector.TOKENS_AFTER_TITLE]
                if span_token.dep_ != "punct" and span_token.tag_ in ("NNP", "NN", "NNPS",) and
                   span_token.is_stop is False
            ]

            if len(span_obj) > 1:
                # create slice with spacy span to include new entity
                entity = Span(doc, min(span_obj), max(span_obj) + 1, label="PERSON")
                # update spacy ents to include the new entity
                doc._.person_titles.append(entity)
    return doc


class SpacyNameTitleDetector(SpacyEntityDetector):
    """Add an extension to the spacy detector to detect titles infront of people's names, eg Mrs J Doe.

    See the ``SpacyDetector`` for further info on how to use this detector.

    Currently only english titles are supported, but other language titles can be easily added, as in the example below:

    >>> import scrubadub, scrubadub.detectors.spacy_name_title
    >>> scrubadub.detectors.spacy_name_title.SpacyNameTitleDetector.NAME_TITLES['de'] = ['frau', 'herr']
    >>> detector = scrubadub.detectors.spacy_name_title.SpacyNameTitleDetector(locale='de_DE', model='de_core_news_sm')
    >>> scrubber = scrubadub.Scrubber(detector_list=[detector], locale='de_DE')
    >>> scrubber.clean("bleib dort Frau Schmidt")
    'bleib dort {{NAME+NAME}}'
    """
    name = "spacy_name_title"

    NAME_TITLES = {
        "en": ['mr', 'mister', 'mrs', 'misses', 'ms', 'miss', 'dr', 'doctor', 'prof', 'professor', 'lord',
               'lady', 'rev', 'reverend', 'hon', 'honourable', 'honorable', 'judge', 'sir', 'madam']
    }

    # This is the number of tokens to look for a name after the title
    TOKENS_AFTER_TITLE = 3

    def __init__(self, **kwargs):
        """Initialise the ``Detector``.

        :param named_entities: Limit the named entities to those in this list, defaults to ``{'PERSON', 'PER', 'ORG'}``
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

        super(SpacyNameTitleDetector, self).__init__(**kwargs)

        Doc.set_extension('person_titles', default=None, force=True)
        self.expand_person_titles = True

        # Add the expand person title component after the named entity recognizer
        self.nlp.add_pipe('expand_person_entities', after='ner')

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
        preprocessed_docs = list(copy.copy(document_list))
        # If the model is a transformer model, we need to transform our data a little to avoid a maximum width of the
        # transformer. Lots of spaces causes lots of tokens to be made and passed to the transformer which makes an
        # index go out of range and so we remove excess whitespace.
        if self.preprocess_text:
            preprocessed_docs = self._preprocess_text(preprocessed_docs)

        spacy_docs = self._run_spacy(document_list=preprocessed_docs, document_names=document_names)

        self.yielded_filth = set()
        for doc_name, doc, text in zip(document_names, spacy_docs, document_list):
            for ent in doc._.person_titles:
                yield from self._yield_filth(doc_name, text, ent)
            for ent in doc.ents:
                yield from self._yield_filth(doc_name, text, ent)
        self.yielded_filth = None

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
        return language in SpacyNameTitleDetector.NAME_TITLES


register_detector(SpacyNameTitleDetector, autoload=False)

__all__ = ['SpacyNameTitleDetector']
