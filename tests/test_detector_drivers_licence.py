import unittest

from base import BaseTestCase


class GBDriversTestCase(unittest.TestCase, BaseTestCase):

    def test_gbdrivers_1(self):
        """
        BEFORE: The driving licence number of the claimant is MORGA753116SM91J 01, and a copy of the licence is attached.
        AFTER:  The driving licence number of the claimant is {{DRIVERS_LICENCE}}, and a copy of the licence is attached.
        """
        self.compare_before_after(locale='en_GB')

    def test_gbdrivers_2(self):
        """
        BEFORE: My DVLA NO is MORGA 753116SM91J 01 could you please check.
        AFTER:  My DVLA NO is {{DRIVERS_LICENCE}} could you please check.
        """
        self.compare_before_after(locale='en_GB')

    def test_gbdrivers_3(self):
        """
        BEFORE: My DVLA NO is MORGA753116SM91J01 could you please check.
        AFTER:  My DVLA NO is {{DRIVERS_LICENCE}} could you please check.
        """
        self.compare_before_after(locale='en_GB')

    def test_gbdrivers_4(self):
        """
        BEFORE: My DVLA NO is MORGA 753 116 SM91J 01 could you please check.
        AFTER:  My DVLA NO is {{DRIVERS_LICENCE}} could you please check.
        """
        self.compare_before_after(locale='en_GB')

    def test_gbdrivers_5(self):
        """
        BEFORE: My DVLA NO is MORGA 753116 SM91J01 could you please check.
        AFTER:  My DVLA NO is {{DRIVERS_LICENCE}} could you please check.
        """
        self.compare_before_after(locale='en_GB')
