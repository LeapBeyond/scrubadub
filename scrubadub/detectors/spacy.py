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
        'ORG': OrganizationFilth
    }
    name = 'spacy'

    disallowed_nouns = CanonicalStringSet(["skype"])

    def __init__(self, named_entities: Iterable[str] = {'PERSON'},
                 model: str = "en_core_web_trf", **kwargs):
        # Spacy NER are all upper cased
        self.named_entities = {entity.upper() for entity in named_entities}

        # Fixes a warning message from transformers that is pulled in via spacy
        os.environ['TOKENIZERS_PARALLELISM'] = 'false'
        self.check_spacy_version()

        self.check_spacy_model(model)
        self.nlp = spacy.load(model)
        # Only enable necessary pipes
        self.nlp.select_pipes(enable=["transformer", "tagger", "parser", "ner"])
        super(SpacyEntityDetector, self).__init__(**kwargs)

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
        models = spacy_info.get('pipelines', spacy_info.get('models', None))
        if models is None:
            raise ValueError('Unable to detect spacy models.')

        if model not in models:
            msg.info("Downloading spacy model {}".format(model))
            spacy.cli.download(model)
            spacy_info = spacy.info()
            models = spacy_info.get('pipelines', spacy_info.get('models', None))

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
                                    label=ent.label_)

    def iter_filth(self, text: str, document_name: Optional[str] = None) -> Generator[Filth, None, None]:
        yield from self.iter_filth_documents([document_name], [text])


register_detector(SpacyEntityDetector, autoload=False)
