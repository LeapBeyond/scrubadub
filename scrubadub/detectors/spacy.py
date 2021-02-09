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
from .base import Detector, RegexDetector
from ..filth import Filth, NameFilth, OrganizationFilth, LocationFilth
from ..utils import CanonicalStringSet


class SpacyEntityDetector(Detector):
    """Use spaCy's named entity recognition to identify possible ``Filth``.

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
    filth_cls_map = {
        'FAC': LocationFilth,      # Buildings, airports, highways, bridges, etc.
        'GPE': LocationFilth,      # Countries, cities, states.
        'LOC': LocationFilth,      # Non-GPE locations, mountain ranges, bodies of water.
        'PERSON': NameFilth,       # People, including fictional.
        'PER': NameFilth,          # Bug in french model
        'ORG': OrganizationFilth,  # Companies, agencies, institutions, etc.
    }
    name = 'spacy'
    language_to_model = {
        "zh": "zh_core_web_trf",
        "nl": "nl_core_news_trf",
        "en": "en_core_web_trf",
        "fr": "fr_dep_news_trf",
        "de": "de_dep_news_trf",
        "es": "es_dep_news_trf",
    }

    disallowed_nouns = CanonicalStringSet(["skype"])

    def __init__(self, named_entities: Optional[Iterable[str]] = None,
                 expand_person_titles: Optional[bool] = True,
                 model: Optional[str] = None, **kwargs):
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
        super(SpacyEntityDetector, self).__init__(**kwargs)

        if named_entities is None:
            named_entities = {'PERSON', 'PER', 'ORG'}

        if expand_person_titles is True:
            Doc.set_extension('person_titles', default=None, force=True)
            self.expand_person_titles = True

        # Spacy NER are all upper cased
        self.named_entities = {entity.upper() for entity in named_entities}

        # Fixes a warning message from transformers that is pulled in via spacy
        os.environ['TOKENIZERS_PARALLELISM'] = 'false'
        self.check_spacy_version()

        if model is not None:
            self.model = model
        else:
            if self.language in self.language_to_model:
                self.model = self.language_to_model[self.language]
            else:
                self.model = "{}_core_news_lg".format(self.language)

        self.preprocess_text = self.model.endswith('_trf')

        if not self.check_spacy_model(self.model):
            raise ValueError("Unable to find spacy model '{}'. Is your language supported? "
                             "Check the list of models available here: "
                             "https://github.com/explosion/spacy-models ".format(self.model))

        self.nlp = spacy.load(self.model)

        # If the model doesn't support named entity recognition
        if 'ner' not in [step[0] for step in self.nlp.pipeline]:
            raise ValueError(
                "The spacy model '{}' doesn't support named entity recognition, "
                "please choose another model.".format(self.model)
            )

        # Only enable necessary pipes
        self.nlp.select_pipes(enable=["transformer", "tagger", "parser", "ner"])

        # Add the expand person title component after the named entity recognizer
        if expand_person_titles is True:
            self.nlp.add_pipe('expand_person_entities', after='ner')

    @Language.component("expand_person_entities")
    def expand_person_entities(doc: spacy.tokens.doc.Doc) -> spacy.tokens.doc.Doc:
        """
        This is the spacy method for adding a label on top of the normal named entity labels.
        This method preserves the existing labels as well as creating a new label for expanded person entities.
        The expanded person entities can be retrieved by using the list doc._.person_titles.
        Each item in the list doc._.person_titles is a spacy.tokens.span.Span,
        which contains the start and end locations.

        :return: spacy doc obj
        """

        person_titles = ['mr', 'mister', 'mrs', 'misses', 'ms', 'miss', 'dr', 'doctor', 'prof', 'professor', 'lord',
                         'lady',
                         'rev', 'reverend', 'hon', 'honourable', 'honorable', 'judge', 'sir', 'madam']
        n_tokens = int(3)

        if doc._.person_titles is None:
            doc._.person_titles = []

        for token in doc:
            # if the token is a title
            if token.text.lower() in person_titles:
                # span of title plus n tokens to inspect
                span_obj = []
                try:
                    for span_token in doc[token.i:token.i + n_tokens]:

                        if span_token.dep_ != "punct" and span_token.tag_ in ("NNP", "NN", "NNPS") \
                                and span_token.is_stop == False:
                            span_obj.append(span_token.i)

                except ValueError:
                    for span_token in doc[token.i]:
                        if span_token.dep_ != "punct" and span_token.tag_ in ("NNP", "NN", "NNPS") \
                                and span_token.is_stop == False:
                            span_obj.append(span_token.i)

                if len(span_obj) > 1:
                    # create slice with spacy span to include new entity
                    entity = Span(doc, min(span_obj), max(span_obj) + 1, label="PERSON")
                    # update spacy ents to include the new entity
                    doc._.person_titles.append(entity)
        return doc

    @staticmethod
    def check_spacy_version() -> bool:
        """Ensure that the version od spaCy is v3."""
        spacy_version = spacy.__version__  # spacy_info.get('spaCy version', spacy_info.get('spacy_version', None))
        spacy_major = 0

        if spacy_version is None:
            raise ImportError('Spacy v3 needs to be installed. Unable to detect spacy version.')
        try:
            spacy_major = int(spacy_version.split('.')[0])
        except Exception:
            raise ImportError('Spacy v3 needs to be installed. Spacy version {} is unknown.'.format(spacy_version))
        if spacy_major != 3:
            raise ImportError('Spacy v3 needs to be installed. Detected version {}.'.format(spacy_version))

        return True

    @staticmethod
    def check_spacy_model(model) -> bool:
        """Ensure that the spaCy model is installed."""
        try:
            spacy_info = spacy.info()
        except TypeError:
            # There is a forgotten default argument in spacy.info in version 3rc3, this try except should be removed
            # in the future. Fixed in spacy v3rc5.
            spacy_info = spacy.info(exclude=[])
        models = list(spacy_info.get('pipelines', spacy_info.get('models', None)).keys())
        if models is None:
            raise ValueError('Unable to detect spacy models.')

        if model not in models:
            msg.info("Downloading spacy model {}".format(model))
            spacy.cli.download(model)
            importlib.import_module(model)
            # spacy.info() doesnt update after a spacy.cli.download, so theres no point checking it
            models.append(model)

        # Always returns true, if it fails to download, spacy sys.exit()s
        return model in models

    @staticmethod
    def _preprocess_text(document_list: List[str]) -> List[str]:
        whitespace_regex = re.compile(r'\s+')
        for i_doc, text in enumerate(document_list):
            document_list[i_doc] = re.sub(whitespace_regex, ' ', text)
        return document_list

    def iter_filth_documents(self, document_list: Sequence[str],
                             document_names: Sequence[Optional[str]]) -> Generator[Filth, None, None]:
        """Yields discovered filth in a list of documents.

        :param document_list: A list of documents to clean.
        :type document_list: List[str]
        :param document_names: A list containing the name of each document.
        :type document_names: List[str]
        :return: An iterator to the discovered :class:`Filth`
        :rtype: Iterator[:class:`Filth`]
        """
        preprocessed_docs = list(copy.copy(document_list))
        # If the model is a transformer model, we need to transform our data a little to avoid a maximum width of the
        # transformer. Lots of spaces causes lots of tokens to be made and passed to the transformer which makes an
        # index go out of range and so we remove excess whitespace.
        if self.preprocess_text:
            preprocessed_docs = self._preprocess_text(preprocessed_docs)

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
            for ent in doc.ents:
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

            if self.expand_person_titles is True:
                for ent in doc._.person_titles:
                    if ent.label_ not in self.named_entities:
                        continue
                    filth_class = self.filth_cls_map.get(ent.label_, Filth)
                    yield filth_class(
                        beg=ent.start,
                        end=ent.end,
                        text=ent.text,
                        document_name=(str(doc_name) if doc_name else None),  # None if no doc_name provided
                        detector_name=self.name,
                        locale=self.locale,
                    )

    def iter_filth(self, text: str, document_name: Optional[str] = None) -> Generator[Filth, None, None]:
        """Yields discovered filth in the provided ``text``.

        :param text: The dirty text to clean.
        :type text: str
        :param document_name: The name of the document to clean.
        :type document_name: str, optional
        :return: An iterator to the discovered :class:`Filth`
        :rtype: Iterator[:class:`Filth`]
        """
        yield from self.iter_filth_documents(document_list=[text], document_names=[document_name])

    @classmethod
    def supported_locale(cls, locale: str) -> bool:
        """Returns true if this ``Detector`` supports the given locale.

        :param locale: The locale of the documents in the format: 2 letter lower-case language code followed by an
                       underscore and the two letter upper-case country code, eg "en_GB" or "de_CH".
        :type locale: str
        :return: ``True`` if the locale is supported, otherwise ``False``
        :rtype: bool
        """
        return True


register_detector(SpacyEntityDetector, autoload=False)

__all__ = ['SpacyEntityDetector']
