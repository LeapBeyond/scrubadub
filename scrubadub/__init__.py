
# convenient imports
from .scrubbers import Scrubber
from . import filth
from . import detectors

__version__ = VERSION = "1.3.0"


def clean(text, cls=None, **kwargs):
    """Public facing function to clean ``text`` using the scrubber ``cls`` by
    replacing all personal information with ``{{PLACEHOLDERS}}``.
    """
    cls = cls or Scrubber
    scrubber = cls()
    return scrubber.clean(text, **kwargs)


def scan(text, cls=None, **kwargs):
    """Public function to check for ``text`` using the scrubber ``cls``"""
    cls = cls or Scrubber
    scrubber = cls()
    return scrubber.scan(text, **kwargs)
