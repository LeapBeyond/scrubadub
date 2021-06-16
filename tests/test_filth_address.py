
import random
import unittest

from scrubadub.filth import AddressFilth


class AddressFilthTestCase(unittest.TestCase):

    def test_generate(self):
        class Faker:
            locales = ['en_GB']
            def address(self):
                return '4 Paula views\nLake Howardburgh\nN7U 2FQ'
            def last_name(self):
                return 'Smith'

        random.seed(1234)
        self.assertEqual(
            'Building Smith, 4 Paula views, Lake Howardburgh, N7U 2FQ, Cymru',
            AddressFilth.generate(faker=Faker()),
        )

    def test_seperators(self):
        addresses = [
            ('4 Paula views\nLake Howardburgh\nN7U 2FQ', '4 Paula views Lake Howardburgh N7U 2FQ'),
            ('79 Miller branch\nJordantown\nW1F 3LB', '79 Miller branch, Jordantown, W1F 3LB'),
            ('78 Joseph keys\nEast Patricktown\nEN6 2SD', '78 Joseph keys, East Patricktown, EN6 2SD'),
            ('93 Hall overpass\nNashbury\nTA2W 9XP', '93 Hall overpass, Nashbury, TA2W 9XP'),
            ('Flat 98R\nNatasha fall\nLake Rosie\nB73 8PJ', 'Flat 98R\nNatasha fall\nLake Rosie\nB73 8PJ'),
            ('8 Roberts stravenue\nElliottville\nSY18 2YP', '8 Roberts stravenue, Elliottville, SY18 2YP'),
            ('784 Knowles mall\nJunetown\nIM20 2PG', '784 Knowles mall, Junetown, IM20 2PG'),
        ]
        random.seed(1234)
        for input_value, output_value in addresses:
            self.assertEqual(
                output_value,
                AddressFilth._randomise_seperators(input_value),
            )

    def test_street_number(self):
        addresses = [
            ('4 Paula views\nLake Howardburgh\nN7U 2FQ', '4 Paula views\nLake Howardburgh\nN7U 2FQ'),
            ('79 Miller branch\nJordantown\nW1F 3LB', 'Miller branch\nJordantown\nW1F 3LB'),
            ('78 Joseph keys\nEast Patricktown\nEN6 2SD', 'Joseph keys\nEast Patricktown\nEN6 2SD'),
            ('93 Hall overpass\nNashbury\nTA2W 9XP', 'Hall overpass\nNashbury\nTA2W 9XP'),
            ('Flat 98R\nNatasha fall\nLake Rosie\nB73 8PJ', 'Flat 98R\nNatasha fall\nLake Rosie\nB73 8PJ'),
            ('8 Roberts stravenue\nElliottville\nSY18 2YP', 'Roberts stravenue\nElliottville\nSY18 2YP'),
            ('784 Knowles mall\nJunetown\nIM20 2PG', '784 Knowles mall\nJunetown\nIM20 2PG'),
        ]
        random.seed(1234)
        for input_value, output_value in addresses:
            self.assertEqual(
                output_value,
                AddressFilth._randomise_street_number(input_value),
            )

    def test_postcode(self):
        addresses = [
            ('4 Paula views\nLake Howardburgh\nN7U 2FQ', '4 Paula views\nLake Howardburgh\nN7U 2FQ'),
            ('79 Miller branch\nJordantown\nW1F 3LB', '79 Miller branch\nJordantown'),
            ('78 Joseph keys\nEast Patricktown\nEN6 2SD', '78 Joseph keys\nEast Patricktown'),
            ('93 Hall overpass\nNashbury\nTA2W 9XP', '93 Hall overpass\nNashbury'),
            ('Flat 98R\nNatasha fall\nLake Rosie\nB73 8PJ', 'Flat 98R\nNatasha fall\nLake Rosie\nB73 8PJ'),
            ('8 Roberts stravenue\nElliottville\nSY18 2YP', '8 Roberts stravenue\nElliottville'),
            ('784 Knowles mall\nJunetown\nIM20 2PG', '784 Knowles mall\nJunetown'),
        ]
        random.seed(1234)
        for input_value, output_value in addresses:
            self.assertEqual(
                output_value,
                AddressFilth._randomise_postcode(input_value),
            )

    def test_country(self):
        addresses = [
            ('4 Paula views\nLake Howardburgh\nN7U 2FQ', '4 Paula views\nLake Howardburgh\nN7U 2FQ'),
            ('79 Miller branch\nJordantown\nW1F 3LB', '79 Miller branch\nJordantown\nW1F 3LB\nUnited Kingdom'),
            ('78 Joseph keys\nEast Patricktown\nEN6 2SD', '78 Joseph keys\nEast Patricktown\nEN6 2SD\nGB'),
            ('93 Hall overpass\nNashbury\nTA2W 9XP', '93 Hall overpass\nNashbury\nTA2W 9XP'),
            ('Flat 98R\nNatasha fall\nLake Rosie\nB73 8PJ', 'Flat 98R\nNatasha fall\nLake Rosie\nB73 8PJ\nCymru'),
            ('8 Roberts stravenue\nElliottville\nSY18 2YP', '8 Roberts stravenue\nElliottville\nSY18 2YP\nUnited Kingdom'),
            ('784 Knowles mall\nJunetown\nIM20 2PG', '784 Knowles mall\nJunetown\nIM20 2PG'),
        ]
        random.seed(1234)
        for input_value, output_value in addresses:
            self.assertEqual(
                output_value,
                AddressFilth._randomise_country(input_value),
            )

    def test_building(self):
        class Faker:
            def last_name(self):
                return 'Smith'

        addresses = [
            ('4 Paula views\nLake Howardburgh\nN7U 2FQ', '4 Paula views\nLake Howardburgh\nN7U 2FQ'),
            ('79 Miller branch\nJordantown\nW1F 3LB', 'Building Smith\n79 Miller branch\nJordantown\nW1F 3LB'),
            ('78 Joseph keys\nEast Patricktown\nEN6 2SD', 'Smith Block\n78 Joseph keys\nEast Patricktown\nEN6 2SD'),
            ('93 Hall overpass\nNashbury\nTA2W 9XP', 'House Smith\n93 Hall overpass\nNashbury\nTA2W 9XP'),
            ('Flat 98R\nNatasha fall\nLake Rosie\nB73 8PJ', 'Flat 98R\nNatasha fall\nLake Rosie\nB73 8PJ'),
            ('8 Roberts stravenue\nElliottville\nSY18 2YP', 'Building Smith\n8 Roberts stravenue\nElliottville\nSY18 2YP'),
            ('784 Knowles mall\nJunetown\nIM20 2PG', '784 Knowles mall\nJunetown\nIM20 2PG'),
        ]
        random.seed(1234)
        for input_value, output_value in addresses:
            self.assertEqual(
                output_value,
                AddressFilth._randomise_building(input_value, faker=Faker()),
            )

    def test_case(self):
        addresses = [
            ('4 Paula views\nLake Howardburgh\nN7U 2FQ', '4 PAULA VIEWS\nLAKE HOWARDBURGH\nN7U 2FQ'),
            ('79 Miller branch\nJordantown\nW1F 3LB', '79 Miller branch\nJordantown\nW1F 3LB'),
            ('78 Joseph keys\nEast Patricktown\nEN6 2SD', '78 Joseph keys\nEast Patricktown\nEN6 2SD'),
            ('93 Hall overpass\nNashbury\nTA2W 9XP', '93 HALL OVERPASS\nNASHBURY\nTA2W 9XP'),
            ('Flat 98R\nNatasha fall\nLake Rosie\nB73 8PJ', 'FLAT 98R\nNATASHA FALL\nLAKE ROSIE\nB73 8PJ'),
            ('8 Roberts stravenue\nElliottville\nSY18 2YP', '8 Roberts stravenue\nElliottville\nSY18 2YP'),
            ('784 Knowles mall\nJunetown\nIM20 2PG', '784 Knowles mall\nJunetown\nIM20 2PG'),
        ]
        random.seed(1234)
        for input_value, output_value in addresses:
            self.assertEqual(
                output_value,
                AddressFilth._randomise_case(input_value),
            )
