import unittest

from base import BaseTestCase


class CreditCardTestCase(unittest.TestCase, BaseTestCase):
    """
    Test cases for Credit Card number removal removal.
    All these will clash with PASSPORT filth.
    """

    def test_american_express(self):
        """
        BEFORE: My credit card is 378282246310005.
        AFTER:  My credit card is {{CREDIT_CARD}}.
        """
        self.compare_before_after()

    def test_american_express2(self):
        """
        BEFORE: My credit card is 371449635398431.
        AFTER:  My credit card is {{CREDIT_CARD}}.
        """
        self.compare_before_after()

    def test_american_corporate(self):
        """
        BEFORE: My credit card is 378734493671000.
        AFTER:  My credit card is {{CREDIT_CARD}}.
        """
        self.compare_before_after()

    def test_diners_club(self):
        """
        BEFORE: My credit card is 30569309025904.
        AFTER:  My credit card is {{CREDIT_CARD}}.
        """
        self.compare_before_after()

    def test_diners_club2(self):
        """
        BEFORE: My credit card is 38520000023237.
        AFTER:  My credit card is {{CREDIT_CARD}}.
        """
        self.compare_before_after()

    def test_discover(self):
        """
        BEFORE: My credit card is 6011111111111117.
        AFTER:  My credit card is {{CREDIT_CARD}}.
        """
        self.compare_before_after()

    def test_discover2(self):
        """
        BEFORE: My credit card is 6011000990139424.
        AFTER:  My credit card is {{CREDIT_CARD}}.
        """
        self.compare_before_after()

    def test_jcb(self):
        """
        BEFORE: My credit card is 3530111333300000.
        AFTER:  My credit card is {{CREDIT_CARD}}.
        """
        self.compare_before_after()

    def test_jcb2(self):
        """
        BEFORE: My credit card is 3566002020360505.
        AFTER:  My credit card is {{CREDIT_CARD}}.
        """
        self.compare_before_after()

    def test_mastercard(self):
        """
        BEFORE: My credit card is 5555555555554444.
        AFTER:  My credit card is {{CREDIT_CARD}}.
        """
        self.compare_before_after()

    def test_mastercard2(self):
        """
        BEFORE: My credit card is 5105105105105100.
        AFTER:  My credit card is {{CREDIT_CARD}}.
        """
        self.compare_before_after()

    def test_visa(self):
        """
        BEFORE: My credit card is 4111111111111111.
        AFTER:  My credit card is {{CREDIT_CARD}}.
        """
        self.compare_before_after()

    def test_visa2(self):
        """
        BEFORE: My credit card is 4012888888881881.
        AFTER:  My credit card is {{CREDIT_CARD}}.
        """
        self.compare_before_after()
