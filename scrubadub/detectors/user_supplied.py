from typing import Optional

from scrubadub.detectors.catalogue import register_detector
from .. import filth as filth_module
from ..filth.base import Filth
from .tagged import TaggedEvaluationFilthDetector


@register_detector
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

    This detector takes a list of dictonaires (reffered to as known filth items). These specify what to look for in
    the text to label as tagged filth. The dictionary should contain the following keys:

        * ``match`` (`str`) - a string value that will be searched for in the text
        * ``filth_type`` (`str`) - a string value that indicates the type of Filth, should be set to ``Filth.name``.
          An example of these could be 'name' or 'phone' for name and phone filths respectively.

    The known filth item dictionary may also optionally contain:

        * ``match_end`` (`str`) - if specified will search for Filth starting with the value of match and ending with
          the value of ``match_end``
        * ``limit`` (`int`) - an integer describing the maximum number of characters between match and match_end,
          defaults to 150
        * ``ignore_case`` (`bool`) - Ignore case when searching for the tagged filth
        * ``ignore_whitespace`` (`bool`) - Ignore whitespace when matching ("asd qwe" can also match "asd\\\\nqwe")
        * ``ignore_partial_word_matches`` (`bool`) - Ignore matches that are only partial words (if you're looking
          for "Eve", this flag ensure it wont match "Evening")

    Examples of this:

        * ``{'match': 'aaa', 'filth_type': 'name'}`` - will search for an exact match to aaa and return it as a
          ``NameFilth``
        * ``{'match': 'aaa', 'match_end': 'zzz', 'filth_type': 'name'}`` - will search for `aaa` followed by up to 150
          characters followed by `zzz`, which would match both `aaabbbzzz` and `aaazzz`.
        * ``{'match': '012345', 'filth_type': 'phone', 'ignore_partial_word_matches': True}`` - will search for an
          exact match to 012345, ignoring any partial matches and return it as a ``PhoneFilth``

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
                filth_cls = filth_module.__getattribute__(item_name)
            except AttributeError:
                continue

            if not isinstance(filth_cls, type) or not issubclass(filth_cls, Filth):
                continue

            try:
                filth_type = filth_cls.type
            except AttributeError:
                continue

            if filth_type != comparison_type:
                continue

            return filth_cls(
                start_location,
                end_location,
                text,
                detector_name=detector_name,
                document_name=document_name,
                locale=locale,
            )
        raise KeyError(f"Unable to find filth '{comparison_type}'")
