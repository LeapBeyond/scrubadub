import re

from .base import RegexDetector
from ..filth import CreditCardFilth
from scrubadub.detectors.catalogue import register_detector


@register_detector
class CreditCardDetector(RegexDetector):
    """Remove credit-card numbers from dirty dirty ``text``.

    Supports Visa, MasterCard, American Express, Diners Club and JCB.
    """
    name = 'credit_card'
    filth_cls = CreditCardFilth
    autoload = True

    # Regexes from:
    # http://www.regular-expressions.info/creditcard.html

    # Fake card numbers from:
    # https://www.paypalobjects.com/en_US/vhelp/paypalmanager_help/credit_card_numbers.htm

    # taken from the alphagov fork of scrubadub: https://github.com/alphagov/scrubadub

    # Looking at wikipedia, there are probably more numbers to detect:
    # https://en.wikipedia.org/wiki/Payment_card_number#Issuer_identification_number_.28IIN.29

    # TODO: regex doesn't match if the credit card number has spaces/dashes in

    regex = re.compile((
        r"(?<=\s)"
        r"(?:4[0-9]{12}(?:[0-9]{3})?"  		# Visa
        r"|(?:5[1-5][0-9]{2}"          		# MasterCard
        r"|222[1-9]|22[3-9][0-9]|2[3-6][0-9]{2}|27[01][0-9]|2720)[0-9]{12}"
        r"|3[47][0-9]{13}"             		# American Express
        r"|3(?:0[0-5]|[68][0-9])[0-9]{11}"   	# Diners Club
        r"|6(?:011|5[0-9]{2})[0-9]{12}"      	# Discover
        r"|(?:2131|1800|35\d{3})\d{11})"      	# JCB
    ), re.VERBOSE)
