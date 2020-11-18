import unittest
import scrubadub
import scrubadub.utils


class LocaleTestCase(unittest.TestCase):

    def test_top_level(self):
        """Test that locales work at the top level"""
        self.assertEqual(
            scrubadub.clean("Localisation is important for phone numbers '06 87 49 77 56'", locale='en_GB'),
            "Localisation is important for phone numbers '06 87 49 77 56'",
        )
        self.assertEqual(
            scrubadub.clean("Localisation is important for phone numbers '06 87 49 77 56'", locale='fr_FR'),
            "Localisation is important for phone numbers '{{PHONE}}'",
        )
        self.assertEqual(
            scrubadub.clean("Localisation is important for phone numbers '(0121) 496 0852'", locale='en_GB'),
            "Localisation is important for phone numbers '{{PHONE}}'",
        )
        self.assertEqual(
            scrubadub.clean("Localisation is important for phone numbers '(0121) 496 0852'", locale='fr_FR'),
            "Localisation is important for phone numbers '(0121) 496 0852'",
        )

    def test_bad_locale(self):
        with self.assertRaises(ValueError):
            scrubadub.clean("Localisation is important for phone numbers '(0121) 496 0852'", locale='non_existant')

    def test_locale_in_filth(self):
        filths = scrubadub.list_filth("Localisation is important for phone numbers '(0121) 496 0852'", locale='en_GB')
        self.assertEqual(len(filths), 1)
        self.assertEqual(filths[0].locale, 'en_GB')

    def test_locale_split(self):
        self.assertEqual(
            scrubadub.utils.locale_split('en_US'),
            ('en', 'US'),
        )
        self.assertEqual(
            scrubadub.utils.locale_split('de_DE'),
            ('de', 'DE'),
        )
        self.assertEqual(
            scrubadub.utils.locale_split('en_GB'),
            ('en', 'GB'),
        )
        self.assertEqual(
            scrubadub.utils.locale_split('en'),
            ('en', 'US'),
        )
        self.assertEqual(
            scrubadub.utils.locale_split('en_GB.ISO8859-1'),
            ('en', 'GB'),
        )
        self.assertEqual(
            scrubadub.utils.locale_split('ru_RU.UTF-8'),
            ('ru', 'RU'),
        )
        self.assertEqual(
            scrubadub.utils.locale_split('tt_RU.UTF-8@iqtelif'),
            ('tt', 'RU'),
        )
        with self.assertRaises(ValueError):
            scrubadub.utils.locale_split('non_existant')

    def test_locale_transform(self):
        with self.assertRaises(ValueError):
            scrubadub.utils.locale_transform('not_exist'),

        self.assertEqual(
            scrubadub.utils.locale_transform('en'),
            'en_US.ISO8859-1',
        )
        self.assertEqual(
            scrubadub.utils.locale_transform('fr'),
            'fr_FR.ISO8859-1',
        )
        self.assertEqual(
            scrubadub.utils.locale_transform('fr_CA'),
            'fr_CA.ISO8859-1',
        )
        self.assertEqual(
            scrubadub.utils.locale_transform('zh'),
            'zh_CN.eucCN',
        )