import sys
from typing import Dict, Type

if sys.version_info >= (3, 8):
    from typing import TypedDict  # pylint: disable=no-name-in-module
else:
    from typing_extensions import TypedDict

from .base import Detector, RegexDetector
from .credential import CredentialDetector
from .credit_card import CreditCardDetector
from .drivers_licence import DriversLicenceDetector
from .email import EmailDetector
from .phone import PhoneDetector
from .postalcode import PostalCodeDetector
from .known import KnownFilthDetector
from .twitter import TwitterDetector
from .url import UrlDetector
from .vehicle_licence_plate import VehicleLicencePlateDetector
from .en_GB.nino import NINODetector
from .en_GB.trn import TrnDetector
from .en_US.social_security_number import SocialSecurityNumberDetector


DetectorConfigurationItem = TypedDict(
    'DetectorConfigurationItem',
    {'detector': Type[Detector], 'autoload': bool}
)

detector_configuration = {
    # Detectors that are automatically loaded by scrubadub
    CredentialDetector.name: {'detector': CredentialDetector, 'autoload': True},
    CreditCardDetector.name: {'detector': CreditCardDetector, 'autoload': True},
    DriversLicenceDetector.name: {'detector': DriversLicenceDetector, 'autoload': True},
    EmailDetector.name: {'detector': EmailDetector, 'autoload': True},
    NINODetector.name: {'detector': NINODetector, 'autoload': True},
    PhoneDetector.name: {'detector': PhoneDetector, 'autoload': True},
    SocialSecurityNumberDetector.name: {'detector': SocialSecurityNumberDetector, 'autoload': True},
    TrnDetector.name: {'detector': TrnDetector, 'autoload': True},
    TwitterDetector.name: {'detector': TwitterDetector, 'autoload': True},
    UrlDetector.name: {'detector': UrlDetector, 'autoload': True},
    VehicleLicencePlateDetector.name: {'detector': VehicleLicencePlateDetector, 'autoload': True},
    # Detectors that are not automatically loaded by scrubadub
    KnownFilthDetector.name: {'detector': KnownFilthDetector, 'autoload': False},
    PostalCodeDetector.name: {'detector': PostalCodeDetector, 'autoload': False},
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

    .. code:: pycon

        >>> import scrubadub
        >>> class NewDetector(scrubadub.detectors.Detector):
        ...     pass
        >>> scrubadub.detectors.register_detector(NewDetector, autoload=False)

    :param detector: The ``Detector`` to register with the scrubadub detector configuration.
    :type detector: Detector class
    :param autoload: Whether to automatically load this ``Detector`` on ``Scrubber`` initialisation.
    :type autoload: bool
    """
    detector_configuration[detector.name] = {
        'detector': detector,
        'autoload': autoload,
    }
    current_module = __import__(__name__)
    setattr(current_module.detectors, detector.__name__, detector)
