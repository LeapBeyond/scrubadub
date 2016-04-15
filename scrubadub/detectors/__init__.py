import os

from ..import_magic import iter_subclasses, update_locals
from .base import Detector


def _is_abstract_detector(detector_cls):
    """Detectors must define a ``filth_cls`` class attribute"""
    return detector_cls.filth_cls is None


def iter_detector_clss():
    """Iterate over all of the detectors that are included in this sub-package.
    This is a convenience method for capturing all new Detectors that are added
    over time and it is used both by the unit tests and in the
    ``Scrubber.__init__`` method.
    """
    return iter_subclasses(
        os.path.dirname(os.path.abspath(__file__)),
        Detector,
        _is_abstract_detector,
    )


def iter_detectors():
    """Iterate over all instances of ``Detector`` subclasses.
    """
    for detector_cls in iter_detector_clss():
        yield detector_cls()


# import all of the detector classes into the local namespace to make it easy
# to do things like `import scrubadub.detectors.NameDetector`
update_locals(locals(), iter_detectors)
