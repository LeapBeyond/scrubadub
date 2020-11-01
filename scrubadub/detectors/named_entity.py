import warnings
from typing import Generator, Iterable, Optional, Sequence

try:
    import spacy
    from wasabi import msg
except ModuleNotFoundError as e:
    if getattr(e, 'name', None) == 'spacy':
        warnings.warn("Could not find module 'spacy'. If you want to use extras,"
                      " make sure you install scrubadub with 'pip install scrubadub[spacy]'")


from .base import Detector
from ..filth import NamedEntityFilth, Filth, NameFilth, OrganizationFilth
from ..utils import CanonicalStringSet


class NamedEntityDetector(Detector):
    """Use spacy's named entity recognition to clean named entities.
     List specific entities to include passing ``named_entities``, e.g.
     (PERSON)
    """
    filth_cls_map = {
        'PERSON': NameFilth,
        'ORG': OrganizationFilth
    }
    name = 'named_entity'

    disallowed_nouns = CanonicalStringSet(["skype"])

    def __init__(self, named_entities: Iterable[str] = {'PERSON'},
                 model: str = "en_core_web_trf", **kwargs):
        # Spacy NER are all upper cased
        self.named_entities = {entity.upper() for entity in named_entities}
        if model not in spacy.info()['pipelines']:
            msg.info("Downloading spacy model {}".format(model))
            spacy.cli.download(model)

        self.nlp = spacy.load(model)
        # Only enable necessary pipes
        self.nlp.select_pipes(enable=["transformer", "tagger", "parser", "ner"])
        super(NamedEntityDetector, self).__init__(**kwargs)

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
