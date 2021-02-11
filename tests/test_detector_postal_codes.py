import pandas as pd
import zipfile
import pathlib
import requests
import unittest
import warnings

import scrubadub

class PostalCodesTestCase(unittest.TestCase):

    def test_bad_locale(self):
        """test a non existant region"""
        with self.assertRaises(ValueError):
            scrubadub.detectors.PostalCodeDetector(locale='non_existant')

    def test_not_implemented_locale(self):
        """test a non existant region"""
        scrubber = scrubadub.Scrubber(locale='fr_FR')
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            with self.assertRaises(UserWarning):
                scrubber.add_detector(scrubadub.detectors.PostalCodeDetector)

    def test_gb(self):
        """test a simple matching"""

        to_test = [
            # positive assertions
            ("BX1 1LT", True),
            ("sw1A 0AA", True),
            ("EC2V 7hh", True),
            ("M25DB", True),
            ("eh12ng", True),
            ("BT1 5GS", True),
            ("EC1A 1BB", True),
            ("W1A 0AX", True),
            ("M1 1AE", True),
            ("B33 8TH", True),
            ("CR2 6XH", True),
            ("DN55 1PT", True),
            ("CM2 0PP", True),
            ("EC3M 5AD", True),
            # negative assertions
            ("1", False),
            ("23", False),
            ("456", False),
            ("4567", False),
            ("750621", False),
            ("95130-642", False),
            ("95130-64212", False),
        ]

        test_str = 'this is a {} test string'
        detector = scrubadub.detectors.PostalCodeDetector(locale='en_GB')

        for postal_code, result in to_test:
            matches = list(detector.iter_filth(test_str.format(postal_code)))
            if result:
                self.assertEquals(len(matches), 1)
                self.assertEquals(matches[0].text, postal_code)
            else:
                self.assertEquals(matches, [])

    def test_extensive(self):
        zip_location = pathlib.Path(__file__).parent / 'code_point_uk_post_codes.zip'

        # Download an extensive list of all postcodes
        if not zip_location.exists():
            url = 'https://api.os.uk/downloads/v1/products/CodePointOpen/downloads?area=GB&format=CSV&redirect'
            r = requests.get(url, allow_redirects=True)
            with open(zip_location.absolute(), 'wb') as f:
                f.write(r.content)

        detector = scrubadub.detectors.PostalCodeDetector(locale='en_GB')

        # Run the detector against this list to ensure we pickup all post codes
        with zipfile.ZipFile(zip_location.absolute()) as zip:
            data_file_names = [
                name for name in zip.namelist()
                if name.lower().endswith('.csv') and name.startswith('Data/CSV')
            ]
            for data_file_name in data_file_names:
                with zip.open(data_file_name) as data_file:
                    df = pd.read_csv(data_file, header=None)
                    post_codes = df.loc[:, 0].sample(frac=.1).values.tolist()
                    for post_code in post_codes:
                        filth_list = list(detector.iter_filth(post_code))
                        error_message = "Unable to match postcode {} from {}".format(post_code, data_file_name)
                        self.assertEquals(1, len(filth_list), error_message)
                        self.assertEquals(post_code, filth_list[0].text)
