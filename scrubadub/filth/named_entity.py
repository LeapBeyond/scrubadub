from .base import Filth


class NamedEntityFilth(Filth):
    """
    Named entity filth. Upon initialisation provide a label for named entity (e.g. name, org)
    """
    type = 'named_entity'

    def __init__(self, *args, label: str, **kwargs):
        super(NamedEntityFilth, self).__init__(*args, **kwargs)
        self.label = label

    def __repr__(self) -> str:
        return self._to_string(['text', 'document_name', 'label'])
