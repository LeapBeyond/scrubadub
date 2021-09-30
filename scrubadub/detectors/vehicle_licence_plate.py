import re

from scrubadub.detectors.catalogue import register_detector
from .base import RegionLocalisedRegexDetector
from ..filth.vehicle_licence_plate import VehicleLicencePlateFilth


@register_detector
class VehicleLicencePlateDetector(RegionLocalisedRegexDetector):
    """Detects standard british licence plates."""
    filth_cls = VehicleLicencePlateFilth
    name = 'vehicle_licence_plate'
    autoload = True

    # Vehicle Registration Plates from:
    # https://gist.github.com/harry-jones/755501192139820eeb65e030fe878f75
    # More cases available in above link, but can cause the regex to become
    # quire greedy. For now keep it simple!

    # taken from the alphagov fork of scrubadub: https://github.com/alphagov/scrubadub

    region_regex = {
        'GB': re.compile(
            # Current system followed by the old system
            r"""
                \b(
                    ([a-zA-Z]{2}[0-9]{2}(?:\s)?[a-zA-Z]{3})
                    |
                    ([a-zA-Z][0-9]{1,3}(?:\s)?[a-zA-Z]{3})
                )\b
            """,
            re.VERBOSE | re.IGNORECASE,
        ),
    }
