import spacy

from typing import List, Optional, Generator

from .base import Detector
from ..filth import NERFilth, Filth
from ..utils import CanonicalStringSet


class SpacyDetector(Detector):
    """Use spacy's named entity recognition to clean named entities.
     List specific entities to include passing ``named_entities``
    """
    filth_cls = NERFilth
    name = 'spacy_ner'

    disallowed_nouns = CanonicalStringSet(["skype"])

    def __init__(self, named_entities: Optional[List[str]] = None, model: str = "en_core_web_trf", **kwargs):
        self.named_entities = named_entities
        if model not in spacy.info()['pipelines']:
            raise OSError(f"Can't find model '{model}'. If it is a valid Spacy model, "
                          f"download it (e.g. with the CLI command "
                          f"`python -m spacy download {model}`).")
        self.nlp = spacy.load(model)
        # Only enable necessary pipes
        self.nlp.select_pipes(enable=["transformer", "tagger", "parser", "ner"])
        super(SpacyDetector, self).__init__(**kwargs)

    def iter_filth(self, text: str, document_name: Optional[str] = None) -> Generator[Filth, None, None]:
        pass
