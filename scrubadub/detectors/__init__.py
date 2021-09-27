from .catalogue import remove_detector, register_detector, detector_catalogue

from .base import Detector, RegexDetector, RegionLocalisedRegexDetector
from .credential import CredentialDetector
from .credit_card import CreditCardDetector
from .date_of_birth import DateOfBirthDetector
from .drivers_licence import DriversLicenceDetector
from .email import EmailDetector
from .phone import PhoneDetector
from .postalcode import PostalCodeDetector
from .skype import SkypeDetector
from .tagged import TaggedEvaluationFilthDetector
from .text_blob import TextBlobNameDetector
from .twitter import TwitterDetector
from .url import UrlDetector
from .user_supplied import UserSuppliedFilthDetector
from .vehicle_licence_plate import VehicleLicencePlateDetector

from . import en_GB
from . import en_US
