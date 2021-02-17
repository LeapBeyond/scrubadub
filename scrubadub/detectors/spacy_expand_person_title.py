import os
import re
import copy
import logging
import importlib

from wasabi import msg
from typing import Generator, Iterable, Optional, Sequence, List

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
from ..filth import Filth, NameFilth
from .base import Detector, RegexDetector
from .spacy import SpacyEntityDetector


class SpacyExpandPersonTitle(SpacyEntityDetector):
    """Use spaCy's named entity recognition to identify and expand ``NameFilth``.

    This looks up tokens that are in a list of person titles, and check the subsequent tokens for any nouns.
    If nouns are found, append the title along with the noun tokens to create a new doc._.person_title entity.
    This detector is made to work with v3 of spaCy, since the NER model has been significantly improved in this
    version.

    This is particularly useful to remove names from text, but can also be used to remove any entity that is
    recognised by spaCy. A full list of entities that spacy supports can be found here:
    `<https://spacy.io/api/annotation#named-entities>`_.

    Additional entities can be added like so:

    >>> import scrubadub, scrubadub.detectors.spacy
    >>> class MoneyFilth(scrubadub.filth.Filth):
    ...     type = 'money'
    >>> scrubadub.detectors.spacy.SpacyEntityDetector.filth_cls_map['MONEY'] = MoneyFilth
    >>> detector = scrubadub.detectors.spacy.SpacyEntityDetector(named_entities=['MONEY'])
    >>> scrubber = scrubadub.Scrubber(detector_list=[detector])
    >>> scrubber.clean("You owe me 12 dollars man!")
    'You owe me {{MONEY}} man!'

    The dictonary ``scrubadub.detectors.spacy.SpacyEntityDetector.filth_cls_map`` is used to map between the spaCy
    named entity label and the type of scrubadub ``Filth``, while the ``named_entities`` argument sets which named
    entities are considered ``Filth`` by the ``SpacyEntityDetector``.
    """
    name = "spacy_expand_person_title"

    def __init__(self, model: str,
                 **kwargs):
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

        super(SpacyExpandPersonTitle, self).__init__(**kwargs)

        self.model = model
        self.nlp = spacy.load(self.model)

        Doc.set_extension('person_titles', default=None, force=True)
        self.expand_person_titles = True

        # Add the expand person title component after the named entity recognizer
        self.nlp.add_pipe('expand_person_entities', after='ner')

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

        person_titles = ['mr', 'mister', 'mrs', 'misses', 'ms', 'miss', 'dr', 'doctor', 'prof', 'professor', 'lord',
                         'lady', 'rev', 'reverend', 'hon', 'honourable', 'honorable', 'judge', 'sir', 'madam']
        n_tokens = int(3)

        if doc._.person_titles is None:
            doc._.person_titles = []

        for token in doc:
            # if the token is a title
            if token.text.lower() in person_titles:
                # span of title plus n tokens to inspect
                span_obj = []
                try:
                    tokens = doc[token.i:token.i + n_tokens]
                except IndexError:
                    for span_token in doc[token.i]:
                        if span_token.dep_ != "punct" and span_token.tag_ in ("NNP", "NN", "NNPS") \
                                and span_token.is_stop is False:
                            span_obj.append(span_token.i)
                else:
                    for span_token in tokens:
                        if span_token.dep_ != "punct" and span_token.tag_ in ("NNP", "NN", "NNPS") \
                                and span_token.is_stop is False:
                            span_obj.append(span_token.i)

                if len(span_obj) > 1:
                    # create slice with spacy span to include new entity
                    entity = Span(doc, min(span_obj), max(span_obj) + 1, label="PERSON")
                    # update spacy ents to include the new entity
                    doc._.person_titles.append(entity)
        return doc

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
        if SpacyEntityDetector._preprocess_text:
            preprocessed_docs = SpacyEntityDetector._preprocess_text(preprocessed_docs)

        i = 0
        spacy_docs = []
        generator = self.nlp.pipe(preprocessed_docs)
        while True:
            try:
                spacy_doc = next(generator)
            except IndexError as e:
                if e.args[0] == 'index out of range in self':
                    message = "Error processing documents due to spacy's transformer model. To use this model, try " \
                              "preprocessing the text by removing non-words and reducing spaces. Skipping file: {}"
                    logger = logging.getLogger('scrubadub.detectors.spacy.SpacyEntityDetector')
                    logger.warning(message.format(document_names[i]))
                    spacy_doc = list(self.nlp.pipe(' '))[0]
                else:
                    raise e
            except StopIteration:
                break
            i += 1
            spacy_docs.append(spacy_doc)

        yielded_filth = set()
        for doc_name, doc, text in zip(document_names, spacy_docs, document_list):

            for ent in doc._.person_titles:

                if ent.label_ not in self.named_entities:
                    continue
                filth_class = self.filth_cls_map.get(ent.label_, Filth)

                if self.preprocess_text:

                    # When yielding the filth we need to yield filth as found in the original un-preprocessed text.
                    # This section searches for text with the inverse of the preprocessing step.
                    if ent.text in yielded_filth:
                        continue
                    yielded_filth.add(ent.text)

                    class SpacyEntDetector(RegexDetector):
                        filth_cls = filth_class
                        regex = re.compile(re.escape(ent.text).replace('\\ ', r'\s+'))

                    regex_detector = SpacyEntDetector(name=self.name, locale=self.locale)
                    yield from regex_detector.iter_filth(text, document_name=doc_name)

                else:
                    # If we didn't pre-process, just return the filth as it was found.
                    yield filth_class(
                        beg=ent.start_char,
                        end=ent.end_char,
                        text=ent.text,
                        document_name=(str(doc_name) if doc_name else None),  # None if no doc_name provided
                        detector_name=self.name,
                        locale=self.locale,
                    )


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
        return language == 'en'


register_detector(SpacyExpandPersonTitle, autoload=False)

__all__ = ['SpacyExpandPersonTitle']
