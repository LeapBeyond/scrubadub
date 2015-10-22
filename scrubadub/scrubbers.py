import re
import operator

import textblob
import nltk

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

        # instantiate all of the detectors
        self.detectors = {}
        for type, detector_cls in detectors.types.iteritems():
            self.detectors[type] = detector_cls()

    def clean(self, text, **kwargs):
        """This is the master method that cleans all of the filth out of the
        dirty dirty ``text``. All keyword arguments to this function are passed
        through to the  ``Filth.replace_with`` method to fine-tune how the
        ``Filth`` is cleaned.
        """
        if not isinstance(text, unicode):
            raise exceptions.UnicodeRequired

        clean_chunks = []
        last_filth = Filth()
        for filth in self.iter_filth(text):
            clean_chunks.append(text[last_filth.end:filth.beg])
            clean_chunks.append(filth.replace_with(**kwargs))
            last_filth = filth
        clean_chunks.append(text[filth.end:])
        return u''.join(clean_chunks)

    def iter_filth(self, text):
        """Iterate over the different types of filth that can exist.
        """
        # TEST: customizing detector behavior. see customize_filth_detection

        # NOTE: we could probably do this in a more efficient way by iterating
        # over all detectors simultaneously. just trying to get something
        # working right now and we can worry about efficiency later
        #
        # TEST: make sure filths are always returned in order from each
        # detector
        all_filths = []
        for detector in self.detectors.itervalues():
            for filth in detector.iter_filth(text):
                # TEST: make sure that this always returns a FILTH object
                all_filths.append(filth)
        # sorting this inline instead of with a Filth.__cmp__ method, which is
        # apparently much slower http://stackoverflow.com/a/988728/564709
        all_filths.sort(key=operator.attrgetter("beg"))

        # need to merge any overlapping filth.
        #
        # TEST: make sure merging works properly
        # TEST: make sure filth is always returned in order from iter_filth
        # TEST: text that has no filth will fail here
        filth = all_filths[0]
        for next_filth in all_filths[1:]:
            if filth.end < next_filth.beg:
                yield filth
                filth = next_filth
            else:
                filth = filth.merge(next_filth)
        yield filth
