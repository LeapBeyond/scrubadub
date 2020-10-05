
from typing import Type, Union, List, Dict, Sequence

# convenient imports
from .scrubbers import Scrubber
from . import filth
from . import detectors
from . import post_processors
from .filth import Filth

__version__ = VERSION = "1.2.2"
__all__ = [
    'Scrubber', 'filth', 'detectors', 'post_processors', 'clean', 'clean_documents', 'list_filth',
    'list_filth_documents',
]


def clean(text: str, cls: Type = None, **kwargs) -> str:
    """Public facing function to clean ``text`` using the scrubber ``cls`` by
    replacing all personal information with ``{{PLACEHOLDERS}}``.
    """
    cls = cls or Scrubber
    scrubber = cls()
    return scrubber.clean(text, **kwargs)


def clean_documents(
        documents: Union[List[str], Dict[str, str]], cls: Type = None, **kwargs
) -> Union[Sequence[str], Dict[str, str]]:
    """Public facing function to clean ``documents`` using the scrubber ``cls`` by
    replacing all personal information with ``{{PLACEHOLDERS}}``.
    """
    cls = cls or Scrubber
    scrubber = cls()
    return scrubber.clean_documents(documents, **kwargs)


def list_filth(text: str, cls: Type = None, **kwargs) -> List[Filth]:
    """Public facing function to clean ``text`` using the scrubber ``cls`` by
    replacing all personal information with ``{{PLACEHOLDERS}}``.
    """
    cls = cls or Scrubber
    scrubber = cls()
    return list(scrubber.iter_filth(text, **kwargs))


def list_filth_documents(documents: Union[List[str], Dict[str, str]], cls: Type = None, **kwargs) -> List[Filth]:
    """Public facing function to clean ``documents`` using the scrubber ``cls`` by
    replacing all personal information with ``{{PLACEHOLDERS}}``.
    """
    cls = cls or Scrubber
    scrubber = cls()
    return list(scrubber.iter_filth_documents(documents, **kwargs))
