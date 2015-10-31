from .name import NameDetector
from .email import EmailDetector
from .url import UrlDetector
from .phone import PhoneDetector
from .credential import CredentialDetector
from .skype import SkypeDetector


# convenience object for instantiating all of the detectors at once
types = {
    "name": NameDetector,
    "email": EmailDetector,
    "url": UrlDetector,
    "phone": PhoneDetector,
    "credential": CredentialDetector,
    "skype": SkypeDetector,
}
