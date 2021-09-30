import warnings
from typing import Optional, Sequence, Generator, Dict, Type, Union, List

from . import detectors
from . import post_processors
from .detectors import Detector
from .post_processors import PostProcessor
from .filth import Filth


class Scrubber:
    """The Scrubber class is used to clean personal information out of dirty
    dirty text. It manages a set of ``Detector``'s that are each responsible
    for identifying ``Filth``. ``PostProcessor`` objects are used to alter
    the found Filth. This could be to replace the Filth with a hash or token.
    """

    def __init__(self, detector_list: Optional[Sequence[Union[Type[Detector], Detector, str]]] = None,
                 post_processor_list: Optional[Sequence[Union[Type[PostProcessor], PostProcessor, str]]] = None,
                 locale: Optional[str] = None):
        """Create a ``Scrubber`` object.

        :param detector_list: The list of detectors to use in this scrubber.
        :type detector_list: Optional[Sequence[Union[Type[Detector], Detector, str]]]
        :param post_processor_list: The locale that the phone number should adhere to.
        :type post_processor_list: Optional[Sequence[Union[Type[Detector], Detector, str]]]
        :param locale: The locale of the documents in the format: 2 letter lower-case language code followed by an
                       underscore and the two letter upper-case country code, eg "en_GB" or "de_CH".
        :type locale: str, optional
        """
        super().__init__()

        # instantiate all of the detectors which, by default, uses all of the
        # detectors that are in the detectors.types dictionary
        self._detectors = {}  # type: Dict[str, Detector]
        self._post_processors = []  # type: List[PostProcessor]

        if locale is None:
            locale = 'en_US'
        self._locale = locale  # type: str

        if detector_list is None:
            # First we gather all detectors that should automatically load
            detector_list = [
                detector
                for detector in detectors.catalogue.detector_catalogue.get_all().values()
                if detector.autoload and (
                    # Then we filter out ones that don't support the current locale
                    not hasattr(detector, 'supported_locale') or (
                        hasattr(detector, 'supported_locale') and
                        detector.supported_locale(locale)  # type: ignore
                    )
                )
            ]

        for detector in detector_list:
            self.add_detector(detector, warn=True)

        if post_processor_list is None:
            post_processor_list = [
                post_processor
                for post_processor in sorted(
                    post_processors.catalogue.post_processor_catalogue.get_all().values(),
                    key=lambda pp: pp.index,
                )
                if post_processor.autoload
            ]

        for post_processor in post_processor_list:
            self.add_post_processor(post_processor)

    def add_detector(self, detector: Union[Detector, Type[Detector], str], warn: bool = True):
        """Add a ``Detector`` to Scrubber

        You can add a detector to a ``Scrubber`` by passing one of three objects to this function:

            1. the uninitalised class to this function, which initialises the class with default settings.
            2. an instance of a ``Detector`` class, where you can initialise it with the settings desired.
            3. a string containing the name of the detector, which again initialises the class with default settings.

        .. code:: pycon

            >>> import scrubadub
            >>> scrubber = scrubadub.Scrubber(detector_list=[])
            >>> scrubber.add_detector(scrubadub.detectors.CreditCardDetector)
            >>> scrubber.add_detector('skype')
            >>> detector = scrubadub.detectors.DateOfBirthDetector(require_context=False)
            >>> scrubber.add_detector(detector)

        :param detector: The ``Detector`` to add to this scrubber.
        :type detector: a Detector class, a Detector instance, or a string with the detector's name
        :param warn: raise a warning if the locale is not supported by the detector.
        :type warn: bool, default True
        """
        if isinstance(detector, type):
            if not issubclass(detector, Detector):
                raise TypeError((
                    '"%(detector)s" is not a subclass of Detector'
                ) % locals())
            self._check_and_add_detector(detector(locale=self._locale), warn=warn)
        elif isinstance(detector, Detector):
            self._check_and_add_detector(detector, warn=warn)
        elif isinstance(detector, str):
            detector_cls = detectors.catalogue.detector_catalogue.get(detector)
            self._check_and_add_detector(detector_cls(locale=self._locale), warn=warn)

    def remove_detector(self, detector: Union[Detector, Type[Detector], str]):
        """Remove a ``Detector`` from a Scrubber

        You can remove a detector from a ``Scrubber`` by passing one of three objects to this function:

            1. the uninitalised class to this function, which removes the initalised detector of the same name.
            2. an instance of a ``Detector`` class, which removes the initalised detector of the same name.
            3. a string containing the name of the detector, which removed the detector of that name.

        .. code:: pycon

            >>> import scrubadub
            >>> scrubber = scrubadub.Scrubber()
            >>> scrubber.remove_detector(scrubadub.detectors.CreditCardDetector)
            >>> scrubber.remove_detector('url')
            >>> detector = scrubadub.detectors.email.EmailDetector()
            >>> scrubber.remove_detector(detector)

        :param detector: The ``Detector`` to remove from this scrubber.
        :type detector: a Detector class, a Detector instance, or a string with the detector's name
        """
        if isinstance(detector, type):
            self._detectors.pop(detector().name)
        elif isinstance(detector, detectors.base.Detector):
            self._detectors.pop(detector.name)
        elif isinstance(detector, str):
            self._detectors.pop(detector)

    def _check_and_add_detector(self, detector: Detector, warn: bool = False):
        """Check the types and add the detector to the scrubber"""
        if not isinstance(detector, Detector):
            raise TypeError((
                'The detector "{}" is not an instance of the '
                'Detector class.'
            ).format(detector))

        name = detector.name
        if hasattr(detector, 'supported_locale'):
            if not detector.supported_locale(self._locale):  # type: ignore
                if warn:
                    warnings.warn("Detector {} does not support the scrubber locale '{}'.".format(name, self._locale))
        if name in self._detectors:
            raise KeyError((
                'can not add Detector "%(name)s" to this Scrubber, this name is already in use. '
                'Try removing it first.'
            ) % locals())
        self._detectors[name] = detector

    def add_post_processor(self, post_processor: Union[PostProcessor, Type[PostProcessor], str], index: int = None):
        """Add a ``PostProcessor`` to a Scrubber

        You can add a post-processor to a ``Scrubber`` by passing one of three objects to this function:

            1. the uninitalised class to this function, which initialises the class with default settings.
            2. an instance of a ``PostProcessor`` class, where you can initialise it with the settings desired.
            3. a string containing the name of the detector, which again initialises the class with default settings.

        .. code:: pycon

            >>> import scrubadub, scrubadub.post_processors
            >>> scrubber = scrubadub.Scrubber()
            >>> scrubber.add_post_processor('filth_replacer')
            >>> scrubber.add_post_processor(scrubadub.post_processors.PrefixSuffixReplacer)

        :param post_processor: The ``PostProcessor`` to remove from this scrubber.
        :type post_processor: a PostProcessor class, a PostProcessor instance, or a string with the post-processor's
            name
        """
        if isinstance(post_processor, type):
            if not issubclass(post_processor, PostProcessor):
                raise TypeError((
                    '"%(post_processor)s" is not a subclass of PostProcessor'
                ) % locals())
            self._check_and_add_post_processor(post_processor(), index=index)
        elif isinstance(post_processor, PostProcessor):
            self._check_and_add_post_processor(post_processor, index=index)
        elif isinstance(post_processor, str):
            if post_processor in post_processors.catalogue.post_processor_catalogue:
                self._check_and_add_post_processor(
                    post_processors.catalogue.post_processor_catalogue.get(post_processor)(), index=index
                )
            else:
                raise ValueError("Unknown PostProcessor: {}".format(post_processor))

    def remove_post_processor(self, post_processor: Union[PostProcessor, Type[PostProcessor], str]):
        """Remove a ``PostProcessor`` from a Scrubber

        You can remove a post-processor from a ``Scrubber`` by passing one of three objects to this function:

            1. the uninitalised class to this function, which removes the initalised post-processor of the same name.
            2. an instance of a ``PostProcessor`` class, which removes the initalised post-processor of the same name.
            3. a string containing the name of the detector, which removed the post-processor of that name.

        .. code:: pycon

            >>> import scrubadub, scrubadub.post_processors
            >>> scrubber = scrubadub.Scrubber()
            >>> scrubber.remove_post_processor('filth_type_replacer')
            >>> scrubber.remove_post_processor(scrubadub.post_processors.PrefixSuffixReplacer)

        :param post_processor: The ``PostProcessor`` to remove from this scrubber.
        :type post_processor: a PostProcessor class, a PostProcessor instance, or a string with the post-processor's
            name
        """
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
        filth_list = list(self.iter_filth(text, document_name=None))  # type: Sequence[Filth]
        filth_list = self._post_process_filth_list(filth_list)
        return self._replace_text(text=text, filth_list=filth_list, document_name=None, **kwargs)

    def clean_documents(self, documents: Union[Sequence[str], Dict[Optional[str], str]], **kwargs) -> \
            Union[Dict[Optional[str], str], Sequence[str]]:
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
        if isinstance(documents, (list, dict)):
            filth_list = list(self.iter_filth_documents(documents=documents, run_post_processors=True))
        else:
            raise TypeError(
                'documents type should be one of: list of strings or a dict of strings with the key as the '
                'document title.'
            )

        if isinstance(documents, list):
            clean_documents = [
                self._replace_text(text=text, filth_list=filth_list, document_name=str(name), **kwargs)
                for name, text in enumerate(documents)
            ]  # type: Union[Dict[Optional[str], str], Sequence[str]]
        elif isinstance(documents, dict):
            clean_documents = {
                name: self._replace_text(text=text, filth_list=filth_list, document_name=name, **kwargs)
                for name, text in documents.items()
            }

        return clean_documents

    def _replace_text(
            self, text: str, filth_list: Sequence[Filth], document_name: Optional[str], **kwargs
    ) -> str:
        filth_list = [filth for filth in filth_list if filth.document_name == document_name]
        if len(filth_list) == 0:
            return text

        filth_list = self._sort_filths(filth_list)  # TODO: expensive sort may not be needed
        filth = None  # type: Optional[Filth]
        clean_chunks = []
        for next_filth in filth_list:
            clean_chunks.append(text[(0 if filth is None else filth.end):next_filth.beg])
            if next_filth.replacement_string is not None:
                clean_chunks.append(next_filth.replacement_string)
            else:
                clean_chunks.append(next_filth.replace_with(**kwargs))
            filth = next_filth
        if filth is not None:
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

    @staticmethod
    def _detector_iter_filth_iterator(detector: Detector, document_list: Sequence[str],
                                      document_names: Sequence[Optional[str]]) -> Generator[Filth, None, None]:
        for doc_name, text in zip(document_names, document_list):
            yield from detector.iter_filth(text, document_name=doc_name)

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
        else:
            raise TypeError(f'documents should be one of dict, list or tuple, but got unsupported type: '
                            f'{type(documents)}')

        # currently doing this by aggregating all_filths and then sorting
        # inline instead of with a Filth.__cmp__ method, which is apparently
        # much slower http://stackoverflow.com/a/988728/564709
        #
        # NOTE: we could probably do this in a more efficient way by iterating
        # over all detectors simultaneously. just trying to get something
        # working right now and we can worry about efficiency later
        filth_list = []  # type: List[Filth]
        for name, detector in self._detectors.items():
            try:
                filth_iterator = detector.iter_filth_documents(
                    document_list=document_texts,
                    document_names=document_names,
                )
            except NotImplementedError:
                filth_iterator = self._detector_iter_filth_iterator(
                    detector=detector,
                    document_list=document_texts,
                    document_names=document_names,
                )

            for filth in filth_iterator:
                if not isinstance(filth, Filth):
                    raise TypeError('iter_filth must always yield Filth')
                if not filth.is_valid():
                    continue
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
            yield from self._merge_filths(filth_list)

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
