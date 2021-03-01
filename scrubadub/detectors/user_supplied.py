from typing import Optional

from .. import filth as filth_module
from ..filth.base import Filth
from .tagged import TaggedEvaluationFilthDetector


class UserSuppliedFilthDetector(TaggedEvaluationFilthDetector):
    """Use this ``Detector`` to find some known filth in the text. An example might be if you have a list of employee
    numbers that you wish to remove from a document, as shown below:

    >>> import scrubadub
    >>> scrubber = scrubadub.Scrubber(detector_list=[
    ...     scrubadub.detectors.UserSuppliedFilthDetector([
    ...         {'match': 'Anika', 'filth_type': 'name'},
    ...         {'match': 'Larry', 'filth_type': 'name'},
    ...     ]),
    ... ])
    >>> scrubber.clean("Anika is my favourite employee.")
    '{{NAME}} is my favourite employee.'

    This detector is not enabled by default (since you need to supply a list of known filths) and so you must always
    add it to your scrubber with a ``scrubber.add_detector(detector)`` call or by adding it to the ``detector_list``
    inialising a ``Scrubber``.
    """

    name = 'user_supplied'

    def create_filth(
            self, start_location: int, end_location: int, text: str, comparison_type: Optional[str],
            detector_name: str, document_name: Optional[str], locale: str
    ) -> Filth:
        for item_name in dir(filth_module):
            try:
                flith_cls = filth_module.__getattribute__(item_name)
            except AttributeError:
                continue

            if not issubclass(flith_cls, Filth):
                continue

            try:
                filth_type = flith_cls.type
            except AttributeError:
                continue

            if filth_type != comparison_type:
                continue

            return flith_cls(
                start_location,
                end_location,
                text,
                detector_name=detector_name,
                document_name=document_name,
                locale=locale,
            )
        raise KeyError(f"Unable to find filth '{comparison_type}'")
