import unittest

import scrubadub
import scrubadub.comparison
from scrubadub.detectors.name import NameDetector
from scrubadub.detectors.predefined import PredefinedDetector

class ComparisonTestCase(unittest.TestCase):

    def test_comparison(self):
        """test a simple matching"""

        test_str = 'Hello John, what are you doing here? john@example.com'
        detector = PredefinedDetector([
            {'match': 'John'},
        ])
        scrubber = scrubadub.Scrubber()
        scrubber.add_detector(detector)
        filths = list(scrubber.iter_filth(test_str))

        self.assertEquals(
            scrubadub.comparison.compare_detectors(
                filths,
                [NameDetector, PredefinedDetector]
            ),
            {'name': 1.0, 'predefined': 1.0}
        )