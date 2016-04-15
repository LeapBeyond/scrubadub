import os
import re

from ..import_magic import iter_subclasses, update_locals
from .base import Filth, MergedFilth, RegexFilth


def _is_abstract_filth(filth_cls):
    """Filth must have a ``type`` defined"""
    return filth_cls.type is None


def iter_filths():
    """Iterate over all of the filths that are included in this sub-package.
    This is a convenience method for capturing all new Filth that are added
    over time.
    """
    subclass_iterator = iter_subclasses(
        os.path.dirname(os.path.abspath(__file__)),
        Filth,
        _is_abstract_filth,
    )
    for subclass in subclass_iterator:
        if issubclass(subclass, RegexFilth):
            m = re.finditer(r"\s+", "fake pattern string").next()
            yield subclass(m)
        else:
            yield subclass()

# import all of the detector classes into the local namespace to make it easy
# to do things like `import scrubadub.detectors.NameDetector`
update_locals(locals(), iter_filths)
