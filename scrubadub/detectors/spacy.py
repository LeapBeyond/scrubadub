import os
import re
import copy
import logging
import importlib
from . import url

from wasabi import msg
from typing import Generator, Iterable, Optional, Sequence, List, Callable, cast, Type

try:
    import spacy
    import spacy.tokens
    import spacy.cli
except ImportError as e:
    if e.name == "spacy":
        raise ImportError(
            "Could not find module 'spacy'. If you want to use extras,"
            " make sure you install scrubadub with 'pip install scrubadub[spacy]'"
        )

from . import register_detector
from .base import Detector, RegexDetector
from ..filth import Filth, NameFilth, OrganizationFilth, LocationFilth, DateOfBirthFilth
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
        'DATE': DateOfBirthFilth,  # Dates within the period 18 to 100 years ago.
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

    @staticmethod
    def check_spacy_version() -> bool:
        """Ensure that the version od spaCy is v3."""
        spacy_version = spacy.__version__  # spacy_info.get('spaCy version', spacy_info.get('spacy_version', None))

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
        spacy_info = spacy.info()
        if isinstance(spacy_info, str):
            raise ValueError('Unable to detect spacy models.')
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
            document_list[i_doc] = re.sub(url.UrlDetector.regex, ' ', document_list[i_doc])
        return document_list

    def _run_spacy(
            self, document_list: Sequence[str], document_names: Sequence[Optional[str]]
    ) -> List[spacy.tokens.doc.Doc]:
        i = 0
        spacy_docs = []  # type: List[spacy.tokens.doc.Doc]

        import spacy_transformers.pipeline_component
        transformer_stages = [stage for name, stage in self.nlp.pipeline if name == 'transformer']
        if len(transformer_stages) > 0:
            transformer_model = cast(spacy_transformers.pipeline_component.Transformer, transformer_stages[0])
            if 'tokenizer' in transformer_model.model.attrs:
                tokenizer = transformer_model.model.attrs['tokenizer']
                tokenizer.deprecation_warnings['sequence-length-is-longer-than-the-specified-maximum'] = False

        generator = self.nlp.pipe(document_list)

        if len(transformer_stages) > 0:
            transformer_model = cast(spacy_transformers.pipeline_component.Transformer, transformer_stages[0])
            if 'tokenizer' in transformer_model.model.attrs:
                tokenizer = transformer_model.model.attrs['tokenizer']
                if tokenizer.deprecation_warnings['sequence-length-is-longer-than-the-specified-maximum']:
                    logger = logging.getLogger('scrubadub.detectors.spacy.SpacyEntityDetector')
                    logger.warning(
                        "The documents that triggered the sequence-length-is-longer-than-the-specified-maximum message:"
                        f"\n{document_list}"
                    )

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

        return spacy_docs

    @staticmethod
    def _get_entities(doc: spacy.tokens.doc.Doc) -> Iterable[spacy.tokens.span.Span]:
        return doc.ents

    def _yield_filth(
            self, document_list: Sequence[str], document_names: Sequence[Optional[str]],
            get_entity_function: Optional[Callable[[spacy.tokens.doc.Doc], Iterable[spacy.tokens.span.Span]]] = None,
    ) -> Generator[Filth, None, None]:

        # If the model is a transformer model, we need to pre-process our data a little to avoid hitting the maximum
        # width of the transformer. Lots of spaces causes lots of tokens to be made and passed to the transformer
        # which causes an index go out of range error and so we remove this excess whitespace.
        preprocessed_docs = list(copy.copy(document_list))
        if self.preprocess_text:
            preprocessed_docs = self._preprocess_text(preprocessed_docs)

        spacy_docs = self._run_spacy(document_list=preprocessed_docs, document_names=document_names)

        if get_entity_function is None:
            get_entity_function = self._get_entities

        for doc_name, doc, text in zip(document_names, spacy_docs, document_list):
            # The pre-processing changes the character positions in the text (because we remove excessive whitespace),
            # so this bit of code searches for the found entities in the original text.
            if self.preprocess_text:
                # Here we will keep a list of the filth that we have found already in this document and only search
                # for entities that we've not already searched for in this document. If "Jane" is twice in a document
                # and we loop over each "Jane" entity and search the whole document for "Jane", we would yield 4
                # "Jane"s instead of just the two that are in the text.
                yielded_filth = set()
                for ent in get_entity_function(doc):
                    if ent.text in yielded_filth or ent.label_ not in self.named_entities:
                        continue
                    yielded_filth.add(ent.text)
                    filth_class = self.filth_cls_map.get(ent.label_, None)
                    if filth_class is None:
                        continue

                    # Use a modified version of the regex detector to find the entities in the original document
                    class PreProcessedSpacyEntityDetector(RegexDetector):
                        filth_cls = cast(Type[Filth], filth_class)
                        regex = re.compile(re.escape(ent.text).replace('\\ ', r'\s+'))

                    regex_detector = PreProcessedSpacyEntityDetector(name=self.name, locale=self.locale)
                    yield from regex_detector.iter_filth(text, document_name=doc_name)
            else:
                # If we didn't preprocess, just loop over the entities and yield Filth.
                for ent in get_entity_function(doc):
                    if ent.label_ not in self.named_entities:
                        continue
                    filth_class = self.filth_cls_map.get(ent.label_, None)
                    if filth_class is None:
                        continue
                    filth = filth_class(
                        beg=ent.start_char,
                        end=ent.end_char,
                        text=ent.text,
                        document_name=(str(doc_name) if doc_name else None),  # None if no doc_name provided
                        detector_name=self.name,
                        locale=self.locale,
                    )
                    if not filth.is_valid():
                        continue
                    yield filth

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
        yield from self._yield_filth(document_list, document_names)

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
