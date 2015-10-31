
from .base import RegexDetector
from ..filth import CredentialFilth


class CredentialDetector(RegexDetector):
    """Remove username/password combinations from dirty drity ``text``.
    """
    filth_cls = CredentialFilth
