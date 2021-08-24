import unittest

import catalogue
import scrubadub
import scrubadub.detectors.catalogue


class DetectorConfigTestCase(unittest.TestCase):
    def test_register_detector(self):
        class NewDetector(scrubadub.detectors.Detector):
            name = 'new_detector'

        scrubadub.detectors.catalogue.register_detector(NewDetector, False)
        self.assertTrue(NewDetector.name in scrubadub.detectors.catalogue.detector_catalogue)
        self.assertFalse(NewDetector.autoload)
        self.assertEqual(scrubadub.detectors.catalogue.detector_catalogue.get(NewDetector.name), NewDetector)

        scrubadub.detectors.catalogue.remove_detector(NewDetector)
        with self.assertRaises(catalogue.RegistryError):
            scrubadub.detectors.catalogue.detector_catalogue.get(NewDetector.name)

        scrubadub.detectors.catalogue.register_detector(NewDetector, True)
        self.assertTrue(NewDetector.name in scrubadub.detectors.catalogue.detector_catalogue)
        self.assertTrue(NewDetector.autoload)
        self.assertEqual(scrubadub.detectors.catalogue.detector_catalogue.get(NewDetector.name), NewDetector)

        scrubadub.detectors.catalogue.remove_detector(NewDetector)
