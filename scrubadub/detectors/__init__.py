import sys
from typing import Dict, Type

if sys.version_info >= (3, 8):
    from typing import TypedDict  # pylint: disable=no-name-in-module
else:
    from typing_extensions import TypedDict

from .base import Detector
from .credential import CredentialDetector
from .email import EmailDetector
from .phone import PhoneDetector
from .postalcode import PostalCodeDetector
from .known import KnownFilthDetector
from .ssn import SSNDetector
from .twitter import TwitterDetector
from .url import UrlDetector
from .gbnino import GBNINODetector
from .gb_drivers import GBDriversDetector


DetectorConfigurationItem = TypedDict(
    'DetectorConfigurationItem',
    {'detector': Type[Detector], 'autoload': bool}
)

detector_configuration = {
    # Detectors that are automatically loaded by scrubadub
    CredentialDetector.name: {'detector': CredentialDetector, 'autoload': True},
    EmailDetector.name: {'detector': EmailDetector, 'autoload': True},
    PhoneDetector.name: {'detector': PhoneDetector, 'autoload': True},
    PostalCodeDetector.name: {'detector': PostalCodeDetector, 'autoload': True},
    SSNDetector.name: {'detector': SSNDetector, 'autoload': True},
    TwitterDetector.name: {'detector': TwitterDetector, 'autoload': True},
    UrlDetector.name: {'detector': UrlDetector, 'autoload': True},
    GBNINODetector.name: {'detector': GBNINODetector, 'autoload': True},
    GBDriversDetector.name: {'detector': GBDriversDetector, 'autoload': True},
    # Detectors that are not automatically loaded by scrubadub
    KnownFilthDetector.name: {'detector': KnownFilthDetector, 'autoload': False},
}  # type: Dict[str, DetectorConfigurationItem]


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
