import os

from wasabi import msg
from typing import Generator, Iterable, Optional, Sequence

try:
    import spacy
except ImportError as e:
    if e.name == "spacy":
        raise ImportError(
            "Could not find module 'spacy'. If you want to use extras,"
            " make sure you install scrubadub with 'pip install scrubadub[spacy]'"
        )

from . import register_detector
from .base import Detector
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

        if model is None:
            if self.language in self.language_to_model:
                model = self.language_to_model[self.language]
            else:
                model = "{}_core_news_lg".format(self.language)

        if not self.check_spacy_model(model):
            raise ValueError("Unable to find spacy model '{}'. Is your language supported? "
                             "Check the list of models available here: "
                             "https://github.com/explosion/spacy-models ".format(model))

        self.nlp = spacy.load(model)

        # If the model doesn't support named entity recognition
        if 'ner' not in [step[0] for step in self.nlp.pipeline]:
            raise ValueError(
                "The spacy model '{}' doesn't support named entity recognition, "
                "please choose another model.".format(model)
            )

        # Only enable necessary pipes
        self.nlp.select_pipes(enable=["transformer", "tagger", "parser", "ner"])

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
        spacy_info = spacy.info()
        models = list(spacy_info.get('pipelines', spacy_info.get('models', None)).keys())
        if models is None:
            raise ValueError('Unable to detect spacy models.')

        if model not in models:
            msg.info("Downloading spacy model {}".format(model))
            spacy.cli.download(model)
            # spacy.info() doesnt update after a spacy.cli.download, so theres no point checking it
            models.append(model)

        # Always returns true, if it fails to download, spacy sys.exit()s
        return model in models

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
        for doc_name, doc in zip(document_names, self.nlp.pipe(document_list)):
            for ent in doc.ents:
                if ent.label_ in self.named_entities:
                    # If there is no 'filth' in self.filth_cls_map, don't return a filth
                    filth_cls = self.filth_cls_map.get(ent.label_, Filth)
                    yield filth_cls(
                        beg=ent.start_char,
                        end=ent.end_char,
                        text=ent.text,
                        document_name=(str(doc_name) if doc_name else None),  # None if no doc_name provided
                        detector_name=self.name,
                        label=ent.label_,
                        locale=self.locale
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
