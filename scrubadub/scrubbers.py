import operator
import sys

from . import exceptions
from . import detectors
from .filth import Filth


class Scrubber(object):
    """The Scrubber class is used to clean personal information out of dirty
    dirty text. It manages a set of ``Detector``'s that are each responsible
    for identifying their particular kind of ``Filth``.
    """

    def __init__(self, *args, **kwargs):
        super(Scrubber, self).__init__(*args, **kwargs)

        # instantiate all of the detectors which, by default, uses all of the
        # detectors that are in the detectors.types dictionary
        self._detectors = {}
        for detector_cls in detectors.iter_detector_clss():
            self.add_detector(detector_cls)

    def add_detector(self, detector_cls):
        """Add a ``Detector`` to scrubadub"""
        if not issubclass(detector_cls, detectors.base.Detector):
            raise TypeError((
                '"%(detector_cls)s" is not a subclass of Detector'
            ) % locals())
        # TODO: should add tests to make sure filth_cls is actually a proper
        # filth_cls
        name = detector_cls.filth_cls.type
        if name in self._detectors:
            raise KeyError((
                'can not add Detector "%(name)s"---it already exists. '
                'Try removing it first.'
            ) % locals())
        self._detectors[name] = detector_cls()

    def remove_detector(self, name):
        """Remove a ``Detector`` from scrubadub"""
        self._detectors.pop(name)

    def get_all_filths(self, text):

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

        # Sort by start position. If two filths start in the same place then
        # return the longer one first
        all_filths.sort(key=lambda f: (f.beg, -f.end))

        return all_filths

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
        for next_filth in self.iter_filth_for_clean(text):
            clean_chunks.append(text[filth.end:next_filth.beg])
            clean_chunks.append(next_filth.replace_with(**kwargs))
            filth = next_filth
        clean_chunks.append(text[filth.end:])
        return u''.join(clean_chunks)

    def iter_filth_for_clean(self, text):
        """Iterate over the different types of filth that can exist.
        """
        all_filths = self.get_all_filths(text)

        # this is where the Scrubber does its hard work and merges any
        # overlapping filths.
        if not all_filths:
            raise StopIteration
        filth = all_filths[0]
        for next_filth in all_filths[1:]:
            if filth.end < next_filth.beg:
                yield filth
                filth = next_filth
            else:
                filth = filth.merge(next_filth)
        yield filth

    def scan(self, text):
        """This is the master method that scans for any filter out of the
        dirty dirty ``text``
        """
        if sys.version_info < (3, 0):
            # Only in Python 2. In 3 every string is a Python 2 unicode
            if not isinstance(text, unicode):
                raise exceptions.UnicodeRequired

        matched_filths = []
        for next_filth in self.iter_filth_for_scan(text):
            matched_filths.append(next_filth.type)

        results = list(sorted(set(matched_filths)))
        return results

    def iter_filth_for_scan(self, text):
        """Iterate over the different types of filth that can exist."""
        all_filths = self.get_all_filths(text)

        if not all_filths:
            raise StopIteration
        filth = all_filths[0]
        for next_filth in all_filths[1:]:
            yield filth
            filth = next_filth
        yield filth
