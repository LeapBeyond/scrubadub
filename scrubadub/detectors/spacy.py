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
from ..filth import NamedEntityFilth, Filth, NameFilth, OrganizationFilth
from ..utils import CanonicalStringSet


class SpacyEntityDetector(Detector):
    """Use spacy's named entity recognition to clean named entities.
     List specific entities to include passing ``named_entities``, e.g.
     (PERSON)
    """
    filth_cls_map = {
        'PERSON': NameFilth,
        'PER': NameFilth,
        'ORG': OrganizationFilth
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

    def __init__(self, named_entities: Iterable[str] = {'PERSON', 'PER'},
                 model: Optional[str] = None, **kwargs):
        super(SpacyEntityDetector, self).__init__(**kwargs)

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
        # spacy_info = spacy.info()
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

    def iter_filth_documents(self, doc_names: Sequence[Optional[str]],
                             doc_list: Sequence[str]) -> Generator[Filth, None, None]:
        for doc_name, doc in zip(doc_names, self.nlp.pipe(doc_list)):
            for ent in doc.ents:
                if ent.label_ in self.named_entities:
                    # If there is no standard 'filth', returns a NamedEntity filth
                    filth_cls = self.filth_cls_map.get(ent.label_, NamedEntityFilth)
                    yield filth_cls(beg=ent.start_char,
                                    end=ent.end_char,
                                    text=ent.text,
                                    document_name=(str(doc_name) if doc_name else None),  # None if no doc_name provided
                                    detector_name=self.name,
                                    label=ent.label_,
                                    locale=self.locale)

    def iter_filth(self, text: str, document_name: Optional[str] = None) -> Generator[Filth, None, None]:
        yield from self.iter_filth_documents([document_name], [text])

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
