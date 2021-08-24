from .catalogue import remove_detector, register_detector, detector_catalogue

from .base import Detector, RegexDetector
from .credential import CredentialDetector
from .credit_card import CreditCardDetector
from .drivers_licence import DriversLicenceDetector
from .email import EmailDetector
from .tagged import TaggedEvaluationFilthDetector
from .user_supplied import UserSuppliedFilthDetector
from .phone import PhoneDetector
from .postalcode import PostalCodeDetector
from .twitter import TwitterDetector
from .url import UrlDetector
from .vehicle_licence_plate import VehicleLicencePlateDetector

from .en_GB.national_insurance_number import NationalInsuranceNumberDetector
from .en_GB.tax_reference_number import TaxReferenceNumberDetector
from .en_US.social_security_number import SocialSecurityNumberDetector
