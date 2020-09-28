from typing import Optional, Sequence, Generator, Dict, Type, Union, List

from . import detectors
from . import post_processors
from .detectors import Detector
from .post_processors import PostProcessor
from .filth import Filth


class Scrubber(object):
    """The Scrubber class is used to clean personal information out of dirty
    dirty text. It manages a set of ``Detector``'s that are each responsible
    for identifying their particular kind of ``Filth``.
    """

    def __init__(self, detector_list: Optional[Sequence[Union[Type[Detector], Detector, str]]] = None,
                 post_processor_list: Optional[Sequence[Union[Type[PostProcessor], PostProcessor, str]]] = None):
        super().__init__()

        # instantiate all of the detectors which, by default, uses all of the
        # detectors that are in the detectors.types dictionary
        self._detectors = {}  # type: Dict[str, Detector]
        self._post_processors = []  # type: List[PostProcessor]

        if detector_list is None:
            detector_list = [
                config['detector']
                for name, config in detectors.detector_configuration.items()
                if config['autoload']
            ]

        for detector in detector_list:
            self.add_detector(detector)

        if post_processor_list is None:
            post_processor_list = [
                config['post_processor']
                for config in sorted(
                    post_processors.post_processor_configuration.values(),
                    key=lambda x: x['index'],
                )
                if config['autoload']
            ]

        for post_processor in post_processor_list:
            self.add_post_processor(post_processor)

    def add_detector(self, detector: Union[Detector, Type[Detector], str]):
        """Add a ``Detector`` to scrubadub"""
        if isinstance(detector, type):
            if not issubclass(detector, Detector):
                raise TypeError((
                    '"%(detector)s" is not a subclass of Detector'
                ) % locals())
            self._check_and_add_detector(detector())
        elif isinstance(detector, Detector):
            self._check_and_add_detector(detector)
        elif isinstance(detector, str):
            if detector in detectors.detector_configuration:
                self._check_and_add_detector(detectors.detector_configuration[detector]['detector']())
            else:
                raise ValueError("Unknown Detector: {}".format(detector))

    def _check_and_add_detector(self, detector: Detector):
        """Check the types and add the detector to the scrubber"""
        if not isinstance(detector, Detector):
            raise TypeError((
                'The detector "{}" is not an instance of the '
                'Detector class.'
            ).format(detector))
        name = detector.name
        if name in self._detectors:
            raise KeyError((
                'can not add Detector "%(name)s" to this Scrubber, this name is already in use. '
                'Try removing it first.'
            ) % locals())
        self._detectors[name] = detector

    def remove_detector(self, detector: Union[Detector, Type[Detector], str]):
        """Remove a ``Detector`` from scrubadub"""
        if isinstance(detector, type):
            self._detectors.pop(detector().name)
        elif isinstance(detector, detectors.base.Detector):
            self._detectors.pop(detector.name)
        elif isinstance(detector, str):
            self._detectors.pop(detector)

    def add_post_processor(self, post_processor: Union[PostProcessor, Type[PostProcessor], str], index: int = -1):
        """Add a ``Detector`` to scrubadub"""
        if isinstance(post_processor, type):
            if not issubclass(post_processor, PostProcessor):
                raise TypeError((
                    '"%(post_processor)s" is not a subclass of PostProcessor'
                ) % locals())
            self._check_and_add_post_processor(post_processor())
        elif isinstance(post_processor, PostProcessor):
            self._check_and_add_post_processor(post_processor)
        elif isinstance(post_processor, str):
            if post_processor in detectors.detector_configuration:
                self._check_and_add_post_processor(
                    post_processors.post_processor_configuration[post_processor]['post_processor']()
                )
            else:
                raise ValueError("Unknown PostProcessor: {}".format(post_processor))

    def _check_and_add_post_processor(self, post_processor: PostProcessor, index: int = -1):
        """Check the types and add the PostProcessor to the scrubber"""
        if not isinstance(post_processor, PostProcessor):
            raise TypeError((
                'The PostProcessor "{}" is not an instance of the '
                'PostProcessor class.'
            ).format(post_processor))
        name = post_processor.name
        if name in [pp.name for pp in self._post_processors]:
            raise KeyError((
                'can not add PostProcessor "%(name)s" to this Scrubber, this name is already in use. '
                'Try removing it first.'
            ) % locals())
        self._post_processors.insert(index, post_processor)

    def remove_post_processor(self, post_processor: Union[PostProcessor, Type[PostProcessor], str]):
        """Remove a ``Detector`` from scrubadub"""
        if isinstance(post_processor, type):
            self._post_processors = [x for x in self._post_processors if x.name != post_processor().name]
        elif isinstance(post_processor, post_processors.base.PostProcessor):
            self._post_processors = [x for x in self._post_processors if x.name != post_processor.name]
        elif isinstance(post_processor, str):
            self._post_processors = [x for x in self._post_processors if x.name != post_processor]

    def clean(self, document: Union[str, Sequence[str], Dict[str, str]], **kwargs) -> \
            Union[str, Dict[str, str], Sequence[str]]:
        """This is the master method that cleans all of the filth out of the
        dirty dirty ``text``. All keyword arguments to this function are passed
        through to the  ``Filth.replace_with`` method to fine-tune how the
        ``Filth`` is cleaned.
        """

        # We are collating all Filths so that they can all be passed to the post processing step together.
        # This is needed for some operations within the PostProcesssors.
        # It could be improved if we know which post processors need collated Filths.
        filth_list = self.iter_filth(document)
        for post_processor in self._post_processors:
            if isinstance(filth_list, list):
                if all(isinstance(el, list) for el in filth_list):
                    filth_list = [post_processor.process_filth(filths) for filths in filth_list]
                else:
                    filth_list = post_processor.process_filth(filth_list)
            elif isinstance(filth_list, dict):
                filth_list = {name: post_processor.process_filth(filths) for name, filths in filth_list.items()}

        if isinstance(document, list) and isinstance(filth_list, list):
            return [
                self._clean_text(text=text, filth_list=filth_list[name], document_name=str(name), **kwargs)
                for name, text in enumerate(document)
            ]
        elif isinstance(document, dict) and isinstance(filth_list, dict):
            return {
                name: self._clean_text(text=text, filth_list=filth_list[name], document_name=name, **kwargs)
                for name, text in document.items()
            }
        elif isinstance(document, str) and isinstance(filth_list, list):
            return self._clean_text(text=document, filth_list=filth_list, **kwargs)
        raise TypeError(
            'text type should be one of: string, list of strings or a dict of strings with the key as the '
            'document title.'
        )

    def _clean_text(self, text: str, filth_list: Sequence[Filth], document_name: Optional[str] = None, **kwargs) -> str:
        if document_name is not None:
            filth_list = [filth for filth in filth_list if filth.document_name == document_name]

        filth_list = self._sort_filths(filth_list)  # TODO: expensive sort may not be needed
        clean_chunks = []
        filth = Filth()
        for next_filth in filth_list:
            clean_chunks.append(text[filth.end:next_filth.beg])
            if next_filth.replacement_string is not None:
                clean_chunks.append(next_filth.replacement_string)
            else:
                clean_chunks.append(next_filth.replace_with(**kwargs))
            filth = next_filth
        clean_chunks.append(text[filth.end:])
        return u''.join(clean_chunks)

    def iter_filth(self, document: Union[str, Sequence[str], Dict[str, str]]) -> \
            Union[Sequence[Filth], Dict[str, Sequence[Filth]], Sequence[Sequence[Filth]]]:
        """Iterate over the different types of filth that can exist.
        """
        if isinstance(document, str):
            return list(self._iter_document_filth(document))
        elif isinstance(document, dict):
            return {
                name: list(self._iter_document_filth(text, document_name=name))
                for name, text in document.items()
            }
        elif isinstance(document, list):
            return [
                list(self._iter_document_filth(text, document_name=str(name)))
                for name, text in enumerate(document)
            ]
        raise TypeError('documents must be one of a string, list of strings or dict of strings.')

    def _iter_document_filth(self, text: str, document_name: Optional[str] = None) -> Generator[Filth, None, None]:
        # currently doing this by aggregating all_filths and then sorting
        # inline instead of with a Filth.__cmp__ method, which is apparently
        # much slower http://stackoverflow.com/a/988728/564709
        #
        # NOTE: we could probably do this in a more efficient way by iterating
        # over all detectors simultaneously. just trying to get something
        # working right now and we can worry about efficiency later

        all_filths = []
        for detector in self._detectors.values():
            for filth in detector.iter_filth(text, document_name=document_name):
                if not isinstance(filth, Filth):
                    raise TypeError('iter_filth must always yield Filth')
                all_filths.append(filth)

        for filth in self._merge_filths(all_filths):
            yield filth

    @staticmethod
    def _sort_filths(filth_list: Sequence[Filth]) -> List[Filth]:
        """Sorts a list of filths, needed before merging and concatenating"""
        # Sort by start position. If two filths start in the same place then
        # return the longer one first
        filth_list = list(filth_list)
        filth_list.sort(key=lambda f: (f.beg, -f.end))
        return filth_list

    @staticmethod
    def _merge_filths(filth_list: Sequence[Filth]) -> Generator[Filth, None, None]:
        """Merge a list of filths if the filths overlap"""

        # Sort by start position. If two filths start in the same place then
        # return the longer one first
        filth_list = Scrubber._sort_filths(filth_list)

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
