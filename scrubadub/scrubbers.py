import warnings
from typing import Optional, Sequence, Generator, Dict, Type, Union, List

from . import detectors
from . import post_processors
from .detectors import Detector
from .post_processors import PostProcessor
from .filth import Filth


class Scrubber(object):
    """The Scrubber class is used to clean personal information out of dirty
    dirty text. It manages a set of ``Detector``'s that are each responsible
    for identifying ``Filth``. ``PostProcessor`` objects are used to alter
    the found Filth. This could be to replace the Filth with a hash or token.
    """

    def __init__(self, detector_list: Optional[Sequence[Union[Type[Detector], Detector, str]]] = None,
                 post_processor_list: Optional[Sequence[Union[Type[PostProcessor], PostProcessor, str]]] = None,
                 locale: Optional[str] = None):
        super().__init__()
        """Create a ``Scrubber`` object.

        :param detector_list: The list of detectors to use in this scrubber.
        :type detector_list: Optional[Sequence[Union[Type[Detector], Detector, str]]]
        :param post_processor_list: The locale that the phone number should adhere to.
        :type post_processor_list: Optional[Sequence[Union[Type[Detector], Detector, str]]]
        :param locale: The locale of the documents in the format: 2 letter lower-case language code followed by an
                       underscore and the two letter upper-case country code, eg "en_GB" or "de_CH".
        :type locale: str, optional
        """

        # instantiate all of the detectors which, by default, uses all of the
        # detectors that are in the detectors.types dictionary
        self._detectors = {}  # type: Dict[str, Detector]
        self._post_processors = []  # type: List[PostProcessor]

        if locale is None:
            locale = 'en_US'
        self._locale = locale  # type: str

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
        """Add a ``Detector`` to scrubadub

        You can add a detector to a ``Scrubber`` by passing one of three objects to this function:

            1. the uninitalised class to this function, which initialises the class with default settings.
            2. an instance of a ``Detector`` class, where you can initialise it with the settings desired.
            3. a string containing the name of the detector, which again initialises the class with default settings.

        .. code:: pycon

            >>> import scrubadub, scrubadub.detectors.spacy, scrubadub.detectors.skype
            >>> scrubber = scrubadub.Scrubber()
            >>> scrubber.add_detector(scrubadub.detectors.spacy.SpacyEntityDetector)
            >>> scrubber.add_detector('skype')
            >>> detector = scrubadub.detectors.spacy.SpacyEntityDetector(name='spacy-2', model='en_core_web_sm')
            >>> scrubber.add_detector(detector)

        :param detector: The ``Detector`` to add to this scrubber.
        :type detector: a Detector class, a Detector instance, or a string with the detector's name
        """
        if isinstance(detector, type):
            if not issubclass(detector, Detector):
                raise TypeError((
                    '"%(detector)s" is not a subclass of Detector'
                ) % locals())
            self._check_and_add_detector(detector(locale=self._locale))
        elif isinstance(detector, Detector):
            self._check_and_add_detector(detector)
        elif isinstance(detector, str):
            if detector in detectors.detector_configuration:
                detector_cls = detectors.detector_configuration[detector]['detector']
                self._check_and_add_detector(detector_cls(locale=self._locale))
            else:
                raise ValueError("Unknown Detector: {}".format(detector))

    def remove_detector(self, detector: Union[Detector, Type[Detector], str]):
        """Remove a ``Detector`` from scrubadub"""
        if isinstance(detector, type):
            self._detectors.pop(detector().name)
        elif isinstance(detector, detectors.base.Detector):
            self._detectors.pop(detector.name)
        elif isinstance(detector, str):
            self._detectors.pop(detector)

    def _check_and_add_detector(self, detector: Detector):
        """Check the types and add the detector to the scrubber"""
        if not isinstance(detector, Detector):
            raise TypeError((
                'The detector "{}" is not an instance of the '
                'Detector class.'
            ).format(detector))
        name = detector.name
        if hasattr(detector, 'supported_locale'):
            if not detector.supported_locale(self._locale):  # type: ignore
                warnings.warn("Detector {} does not support the scrubber locale '{}'.".format(name, self._locale))
                return
        if name in self._detectors:
            raise KeyError((
                'can not add Detector "%(name)s" to this Scrubber, this name is already in use. '
                'Try removing it first.'
            ) % locals())
        self._detectors[name] = detector

    def add_post_processor(self, post_processor: Union[PostProcessor, Type[PostProcessor], str], index: int = None):
        """Add a ``Detector`` to scrubadub"""
        if isinstance(post_processor, type):
            if not issubclass(post_processor, PostProcessor):
                raise TypeError((
                    '"%(post_processor)s" is not a subclass of PostProcessor'
                ) % locals())
            self._check_and_add_post_processor(post_processor(), index=index)
        elif isinstance(post_processor, PostProcessor):
            self._check_and_add_post_processor(post_processor, index=index)
        elif isinstance(post_processor, str):
            if post_processor in post_processors.post_processor_configuration:
                self._check_and_add_post_processor(
                    post_processors.post_processor_configuration[post_processor]['post_processor'](), index=index
                )
            else:
                raise ValueError("Unknown PostProcessor: {}".format(post_processor))

    def remove_post_processor(self, post_processor: Union[PostProcessor, Type[PostProcessor], str]):
        """Remove a ``Detector`` from scrubadub"""
        if isinstance(post_processor, type):
            self._post_processors = [x for x in self._post_processors if x.name != post_processor().name]
        elif isinstance(post_processor, post_processors.base.PostProcessor):
            self._post_processors = [x for x in self._post_processors if x.name != post_processor.name]
        elif isinstance(post_processor, str):
            self._post_processors = [x for x in self._post_processors if x.name != post_processor]

    def _check_and_add_post_processor(self, post_processor: PostProcessor, index: int = None):
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
        if index is None:
            self._post_processors.append(post_processor)
        else:
            self._post_processors.insert(index, post_processor)

    def clean(self, text: str, **kwargs) -> str:
        """This is the master method that cleans all of the filth out of the
        dirty dirty ``text``. All keyword arguments to this function are passed
        through to the  ``Filth.replace_with`` method to fine-tune how the
        ``Filth`` is cleaned.
        """
        if 'replace_with' in kwargs:
            warnings.warn("Use of replace_with is depreciated in favour of using PostProcessors", DeprecationWarning)

        # We are collating all Filths so that they can all be passed to the post processing step together.
        # This is needed for some operations within the PostProcesssors.
        # It could be improved if we know which post processors need collated Filths.
        filth_list = list(self.iter_filth(text))  # type: Sequence[Filth]
        filth_list = self._post_process_filth_list(filth_list)
        return self._replace_text(text=text, filth_list=filth_list, **kwargs)

    def clean_documents(self, documents: Union[Sequence[str], Dict[str, str]], **kwargs) -> \
            Union[Dict[str, str], Sequence[str]]:
        """This is the master method that cleans all of the filth out of the
        dirty dirty ``text``. All keyword arguments to this function are passed
        through to the  ``Filth.replace_with`` method to fine-tune how the
        ``Filth`` is cleaned.
        """
        if 'replace_with' in kwargs:
            warnings.warn("Use of replace_with is depreciated in favour of using PostProcessors", DeprecationWarning)

        # We are collating all Filths so that they can all be passed to the post processing step together.
        # This is needed for some operations within the PostProcesssors.
        # It could be improved if we know which post processors need collated Filths.
        filth_list = []  # type: Sequence[Filth]
        if isinstance(documents, list):
            filth_list = [
                filth
                for name, document in enumerate(documents)
                for filth in self.iter_filth(document, document_name=str(name))
            ]
        elif isinstance(documents, dict):
            filth_list = [
                filth
                for name, document in documents.items()
                for filth in self.iter_filth(document, document_name=name)
            ]
        else:
            raise TypeError(
                'documents type should be one of: list of strings or a dict of strings with the key as the '
                'document title.'
            )

        filth_list = self._post_process_filth_list(filth_list)

        if isinstance(documents, list):
            clean_documents = [
                self._replace_text(text=text, filth_list=filth_list, document_name=str(name), **kwargs)
                for name, text in enumerate(documents)
            ]  # type: Union[Dict[str, str], Sequence[str]]
        elif isinstance(documents, dict):
            clean_documents = {
                name: self._replace_text(text=text, filth_list=filth_list, document_name=name, **kwargs)
                for name, text in documents.items()
            }

        return clean_documents

    def _replace_text(
            self, text: str, filth_list: Sequence[Filth], document_name: Optional[str] = None, **kwargs
    ) -> str:
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

    def _post_process_filth_list(self, filth_list: Sequence[Filth]) -> Sequence[Filth]:
        # We are collating all Filths so that they can all be passed to the post processing step together.
        # This is needed for some operations within the PostProcesssors.
        # It could be improved if we know which post processors need collated Filths.
        for post_processor in self._post_processors:
            filth_list = post_processor.process_filth(filth_list)

        return filth_list

    def iter_filth(
            self, text: str, document_name: Optional[str] = None, run_post_processors: bool = True
    ) -> Generator[Filth, None, None]:
        """Iterate over the different types of filth that can exist.
        """
        # Iterates using iter_filth documents.
        # If a name is not provided, passes a list with one element, [text]

        yield from self.iter_filth_documents(documents={document_name: text},
                                             run_post_processors=run_post_processors)

    def iter_filth_documents(
            self,
            documents: Union[Sequence[str], Dict[Optional[str], str]],
            run_post_processors: bool = True
    ) -> Generator[Filth, None, None]:
        """Iterate over the different types of filth that can exist."""
        if not isinstance(documents, (dict, list)):
            raise TypeError('documents must be one of a string, list of strings or dict of strings.')

        # Figures out which detectors have iter_filth_documents and applies to them

        if isinstance(documents, dict):
            document_names = list(documents.keys())
            document_texts = list(documents.values())
        elif isinstance(documents, (tuple, list)):
            document_texts = documents
            document_names = [str(x) for x in range(len(documents))]

        # currently doing this by aggregating all_filths and then sorting
        # inline instead of with a Filth.__cmp__ method, which is apparently
        # much slower http://stackoverflow.com/a/988728/564709
        #
        # NOTE: we could probably do this in a more efficient way by iterating
        # over all detectors simultaneously. just trying to get something
        # working right now and we can worry about efficiency later
        filth_list = []  # type: List[Filth]
        for name, detector in self._detectors.items():
            document_iterator = getattr(detector, 'iter_filth_documents', None)
            if callable(document_iterator):
                for filth in document_iterator(document_names, document_texts):
                    if not isinstance(filth, Filth):
                        raise TypeError('iter_filth must always yield Filth')
                    filth_list.append(filth)
            else:
                for document_name, text in zip(document_names, document_texts):
                    for filth in detector.iter_filth(text, document_name=document_name):
                        if not isinstance(filth, Filth):
                            raise TypeError('iter_filth must always yield Filth')
                        filth_list.append(filth)

        # This is split up so that we only have to use lists if we have to post_process Filth
        if run_post_processors:
            all_filths = list(self._merge_filths(filth_list))
            all_filths = list(self._post_process_filth_list(all_filths))

            # Here we loop over a list of Filth...
            for filth in all_filths:
                yield filth
        else:
            # ... but here, we're using a generator. If we try to use the same variable it would have two types and
            # fail static typing in mypy
            for filth in self._merge_filths(filth_list):
                yield filth

    @staticmethod
    def _sort_filths(filth_list: Sequence[Filth]) -> List[Filth]:
        """Sorts a list of filths, needed before merging and concatenating"""
        # Sort by start position. If two filths start in the same place then
        # return the longer one first
        filth_list = list(filth_list)
        filth_list.sort(key=lambda f: (
            str(getattr(f, 'document_name', None) if hasattr(f, 'document_name') else ''), f.beg, -f.end
        ))
        return filth_list

    @staticmethod
    def _merge_filths(filth_list: Sequence[Filth]) -> Generator[Filth, None, None]:
        """This is where the Scrubber does its hard work and merges any
        overlapping filths.
        """
        if not filth_list:
            return

        document_name_set = {f.document_name for f in filth_list}
        document_names = []  # type: Sequence[Optional[str]]
        if None in document_name_set:
            list_with_none = [None]  # type: Sequence[Optional[str]]
            list_with_others = sorted([x for x in document_name_set if x is not None])  # type: Sequence[Optional[str]]
            document_names = list(list_with_none) + list(list_with_others)
        else:
            document_names = sorted([x for x in document_name_set if x is not None])

        for document_name in document_names:
            document_filth_list = Scrubber._sort_filths([f for f in filth_list if f.document_name == document_name])

            filth = document_filth_list[0]
            for next_filth in document_filth_list[1:]:
                if filth.end < next_filth.beg:
                    yield filth
                    filth = next_filth
                else:
                    filth = filth.merge(next_filth)
            yield filth
