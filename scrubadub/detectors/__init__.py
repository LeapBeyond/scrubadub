import os
import sys

from textblob.blob import BaseBlob
from textblob.en.taggers import PatternTagger
from typing import Dict, Type

if sys.version_info >= (3, 8):
    from typing import TypedDict  # pylint: disable=no-name-in-module
else:
    from typing_extensions import TypedDict

from ..import_magic import iter_subclasses, update_locals
from .base import Detector
from .credential import CredentialDetector
from .email import EmailDetector, NewEmailDetector
from .name import NameDetector
from .phone import PhoneDetector
from .postalcode import PostalCodeDetector
from .known import KnownFilthDetector
from .skype import SkypeDetector
from .ssn import SSNDetector
from .url import UrlDetector


class DetectorConfigurationItem(TypedDict):
    detector: Type[Detector]
    autoload: bool


detector_configuration = {
    # Detectors that are automatically loaded by scrubadub
    CredentialDetector.name: {'detector': CredentialDetector, 'autoload': True},
    EmailDetector.name: {'detector': EmailDetector, 'autoload': True},
    NameDetector.name: {'detector': NameDetector, 'autoload': True},
    NewEmailDetector.name: {'detector': NewEmailDetector, 'autoload': False},
    PhoneDetector.name: {'detector': PhoneDetector, 'autoload': True},
    PostalCodeDetector.name: {'detector': PostalCodeDetector, 'autoload': True},
    SkypeDetector.name: {'detector': SkypeDetector, 'autoload': True},
    SSNDetector.name: {'detector': SSNDetector, 'autoload': True},
    UrlDetector.name: {'detector': UrlDetector, 'autoload': True},
    # Detectors that are not automatically loaded by scrubadub
    KnownFilthDetector.name: {'detector': KnownFilthDetector, 'autoload': False},
}  # type: Dict[str, DetectorConfigurationItem]

# BaseBlob uses NLTKTagger as a pos_tagger, but it works wrong
BaseBlob.pos_tagger = PatternTagger()


def register_detector(detector: Type[Detector], autoload: bool = False):
    """Register a detector for use with the ``Scrubber`` class.

    This is used when you dont want to have to import a detector by default.
    It may be useful for certain detectors with large or unusal dependancies, which you may not always want to import.
    In this case you can use ``register_detector(NewDetector, autoload=True)`` after your detector definition so that
    if the file is imported it wil be automatically registered.
    This will mean that you don't need to import the ``NewDetector`` in this file and so it's dependencies won't need
    to be installed just to import this package.

    The argument ``autoload`` sets if a new ``Scrubber()`` instance should load this ``Detector`` by default.
    """
    detector_configuration[detector.name] = {
        'detector': detector,
        'autoload': autoload,
    }


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
# update_locals(locals(), iter_detectors)
