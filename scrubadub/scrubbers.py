import sys
import typing
import inspect

from . import exceptions
from . import detectors
from .filth import Filth


class Scrubber(object):
    """The Scrubber class is used to clean personal information out of dirty
    dirty text. It manages a set of ``Detector``'s that are each responsible
    for identifying their particular kind of ``Filth``.
    """

    default_detectors = [
        detectors.CredentialDetector,
        detectors.EmailDetector,
        detectors.NameDetector,
        detectors.PhoneDetector,
        detectors.SkypeDetector,
        detectors.SSNDetector,
        detectors.UrlDetector,
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # instantiate all of the detectors which, by default, uses all of the
        # detectors that are in the detectors.types dictionary
        self._detectors = {}
        for detector_cls in self.default_detectors:
            self.add_detector(detector_cls)

    def add_detector(self, detector):
        """Add a ``Detector`` to scrubadub"""
        if inspect.isclass(detector):
            if not issubclass(detector, detectors.base.Detector):
                raise TypeError((
                    '"%(detector)s" is not a subclass of Detector'
                ) % locals())
            self._check_and_add_detector(detector())
        elif isinstance(detector, detectors.base.Detector):
            self._check_and_add_detector(detector)
        elif isinstance(detector, str):
            detector_lookup = {x.filth_cls.type: x for x in self.default_detectors}
            if detector in detector_lookup:
                self._check_and_add_detector(detector_lookup[detector]())
            else:
                raise ValueError("Unknown detector")

    def _check_and_add_detector(self, detector):
        """Check the types and add the detector to the scrubber"""
        if not isinstance(detector, detectors.base.Detector):
            raise TypeError((
                'The detector "{}" is not an instance of the '
                'Detector class.'
            ).format(detector))
        if not issubclass(detector.filth_cls, Filth):
            raise TypeError((
                'The filth_cls "{}" in the detector "{}" is not a subclass '
                'of Filth'
            ).format(detector.filth_cls, detector))
        name = detector.filth_cls.type
        if name in self._detectors:
            raise KeyError((
                'can not add Detector "%(name)s"---it already exists. '
                'Try removing it first.'
            ) % locals())
        self._detectors[name] = detector

    def remove_detector(self, name):
        """Remove a ``Detector`` from scrubadub"""
        self._detectors.pop(name)

    def clean(self, text, **kwargs):
        """This is the master method that cleans all of the filth out of the
        dirty dirty ``text``. All keyword arguments to this function are passed
        through to the  ``Filth.replace_with`` method to fine-tune how the
        ``Filth`` is cleaned.
        """
        if sys.version_info < (3, 0):
            # Only in Python 2. In 3 every string is a Python 2 unicode
            if not isinstance(text, unicode):
                raise exceptions.UnicodeRequired

        clean_chunks = []
        filth = Filth()
        for next_filth in self.iter_filth(text):
            clean_chunks.append(text[filth.end:next_filth.beg])
            clean_chunks.append(next_filth.replace_with(**kwargs))
            filth = next_filth
        clean_chunks.append(text[filth.end:])
        return u''.join(clean_chunks)

    def iter_filth(self, text):
        """Iterate over the different types of filth that can exist.
        """
        # currently doing this by aggregating all_filths and then sorting
        # inline instead of with a Filth.__cmp__ method, which is apparently
        # much slower http://stackoverflow.com/a/988728/564709
        #
        # NOTE: we could probably do this in a more efficient way by iterating
        # over all detectors simultaneously. just trying to get something
        # working right now and we can worry about efficiency later
        all_filths = []
        for detector in self._detectors.values():
            for filth in detector.iter_filth(text):
                if not isinstance(filth, Filth):
                    raise TypeError('iter_filth must always yield Filth')
                all_filths.append(filth)

        for filth in self._merge_filths(all_filths):
            yield filth

    @staticmethod
    def _merge_filths(filth_list: typing.List[Filth]) -> typing.Generator[Filth, None, None]:
        """Merge a list of filths if the filths overlap"""

        # Sort by start position. If two filths start in the same place then
        # return the longer one first
        filth_list.sort(key=lambda f: (f.beg, -f.end))

        # this is where the Scrubber does its hard work and merges any
        # overlapping filths.
        if not filth_list:
            return

        filth = filth_list[0]
        for next_filth in filth_list[1:]:
            if filth.end < next_filth.beg:
                yield filth
                filth = next_filth
            else:
                filth = filth.merge(next_filth)
        yield filth
