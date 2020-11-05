from .base import Filth


class NamedEntityFilth(Filth):
    """
    Default filth type, for named entities (e.g. the ones in https://nightly.spacy.io/models/en#en_core_web_lg-labels),
    except the ones represented in any other filth.
    """
    type = 'named_entity'

    def __init__(self, *args, label: str, **kwargs):
        super(NamedEntityFilth, self).__init__(*args, **kwargs)
        self.label = label.lower()
        self.replacement_string = "{}_{}".format(self.type, self.label)
