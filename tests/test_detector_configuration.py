import unittest
import scrubadub


class DetectorConfigTestCase(unittest.TestCase):
    def test_register_detector(self):
        class NewDetector(scrubadub.detectors.Detector):
            name = 'new_detector'

        scrubadub.detectors.register_detector(NewDetector, False)
        self.assertTrue(NewDetector.name in scrubadub.detectors.detector_configuration)
        self.assertEqual(scrubadub.detectors.detector_configuration[NewDetector.name]['autoload'], False)
        self.assertEqual(scrubadub.detectors.detector_configuration[NewDetector.name]['detector'], NewDetector)

        scrubadub.detectors.detector_configuration.pop(NewDetector.name)
        self.assertTrue(NewDetector.name not in scrubadub.detectors.detector_configuration)

        scrubadub.detectors.register_detector(NewDetector, True)
        self.assertTrue(NewDetector.name in scrubadub.detectors.detector_configuration)
        self.assertEqual(scrubadub.detectors.detector_configuration[NewDetector.name]['autoload'], True)
        self.assertEqual(scrubadub.detectors.detector_configuration[NewDetector.name]['detector'], NewDetector)

        scrubadub.detectors.detector_configuration.pop(NewDetector.name)
