import sys
import copy

from typing import Optional, List, Generator

if sys.version_info >= (3, 8):
    from typing import TypedDict  # pylint: disable=no-name-in-module
else:
    from typing_extensions import TypedDict

from .base import Detector
from ..filth.known import KnownFilth

KnownFilthItem = TypedDict(
    'KnownFilthItem',
    {
        'match': str,
        'match_end': Optional[str],
        'limit': Optional[int],
        'ignore_case': Optional[bool],
        'filth_type': str
    },
    total=False,
)


class KnownFilthDetector(Detector):
    """Use this ``Detector`` to find some known filth in the text.

    This is useful in two situations:

        1. If you have known Filth that you want to remove from text (Such as a list of employee numbers)
        2. If you want evaluate the effectiveness of a Detector using Filth selected by a human.

    An example of how to use this detector is given below:

    >>> import scrubadub, scrubadub.comparison, scrubadub.detectors.text_blob
    >>> scrubber = scrubadub.Scrubber(detector_list=[
    ...     scrubadub.detectors.TextBlobNameDetector(name='name_detector'),
    ...     scrubadub.detectors.KnownFilthDetector([
    ...         {'match': 'Tom', 'filth_type': 'name'},
    ...         {'match': 'tom@example.com', 'filth_type': 'email'},
    ...     ]),
    ... ])
    >>> filth_list = list(scrubber.iter_filth("Hello I am Tom"))
    >>> print(scrubadub.comparison.get_filth_classification_report(filth_list))
    filth          detector     locale    precision    recall  f1-score   support
    <BLANKLINE>
     name     name_detector      en_US         1.00      1.00      1.00         1
    <BLANKLINE>
                                accuracy                           1.00         1
                               macro avg       1.00      1.00      1.00         1
                            weighted avg       1.00      1.00      1.00         1
    <BLANKLINE>

    This detector is not enabled by default (since you need to supply a list of known filths) and so you must always
    add it to your scrubber with a ``scrubber.add_detector(detector)`` call or by adding it to the ``detector_list``
    inialising a ``Scrubber``.
    """

    filth_cls = KnownFilth
    name = 'known'

    def __init__(self, known_filth_items: Optional[List[KnownFilthItem]] = None, **kwargs):
        """Initialise the ``Detector``.

        :param known_filth_items: A list of dictionaries that describe items to be searched for in the dirty text. The
            dictionary should contain the following keys: 'match' (with a string value that will be searched for in the
            text) and 'filth_type' (with a string value that indicates the type of Filth, should be set to
            ``Filth.name``). Optionally the dictionary may also contain: 'match_end' (if specified will search for
            Filth starting with the value of match and ending with the value of match_end) and 'limit' (an integer
            describing the maximum number of characters between match and match_end, defaults to 150). A dictionary
            ``{'match': 'aaa', 'filth_type': 'name'}`` will search for an exact match to aaa and return it as a
            ``NameFilth``, where as ``{'match': 'aaa', 'match_end': 'zzz', 'filth_type': 'name'}`` will search for
            `aaa` followed by up to 150 characters followed by `zzz`, which would match both `aaabbbzzz` and `aaazzz`.
        :type known_filth_items: list of dicts, optional
        :param name: Overrides the default name of the :class:``Detector``
        :type name: str, optional
        :param locale: The locale of the documents in the format: 2 letter lower-case language code followed by an
                       underscore and the two letter upper-case country code, eg "en_GB" or "de_CH".
        :type locale: str, optional
        """
        super().__init__(**kwargs)
        if known_filth_items is None:
            known_filth_items = []

        for item in known_filth_items:
            if 'match' not in item or 'filth_type' not in item:
                raise KeyError("Each known filth item (dict) needs both keys 'match' and 'filth_type'.")
            if not isinstance(item['match'], str):
                raise ValueError("The value of 'match' in each KnownItem should be a string. "
                                 "Current value: " + item['match'].__repr__())
            if 'match_end' in item:
                if not isinstance(item['match_end'], str):
                    raise ValueError("The value of 'match_end' in each KnownItem should be a string. "
                                     "Current value: " + item['match_end'].__repr__())
            for key in item.keys():
                if key not in ['match', 'match_end', 'limit', 'filth_type', 'ignore_case']:
                    raise KeyError("Unexpected key '{}' in the known filth item.".format(key))

        self._known_filth_items = known_filth_items

    def _find_all(
            self,
            text: str,
            substr: str,
            comparison_type: Optional[str] = None,
            document_name: Optional[str] = None,
            ignore_case: bool = False,
    ) -> Generator[KnownFilth, None, None]:
        """Yield filth for each match to substr in text."""

        text_orig = copy.copy(text)
        if ignore_case:
            text = text.lower()
            substr = substr.lower()

        substr_len = len(substr)
        start_location = text.find(substr)

        while start_location >= 0:
            yield KnownFilth(
                start_location,
                start_location + substr_len,
                text_orig[start_location:start_location + substr_len],
                comparison_type=comparison_type,
                detector_name=self.name,
                document_name=document_name,
                locale=self.locale,
            )
            start_location = text.find(
                substr,
                start_location + substr_len
            )

    def _find_all_between(
            self,
            text: str,
            substr_start: str,
            substr_end: str,
            limit: int = 150,
            comparison_type: Optional[str] = None,
            document_name: Optional[str] = None,
            ignore_case: bool = False,
    ) -> Generator[KnownFilth, None, None]:
        """Yield filth for text between (and including)
        substr_start and substr_end, but only if the text
        between the two is less than limit characters.
        """
        text_orig = copy.copy(text)
        if ignore_case:
            text = text.lower()
            substr_start = substr_start.lower()
            substr_end = substr_end.lower()

        substr_start_len = len(substr_start)
        substr_end_len = len(substr_end)
        start_location = text.find(substr_start)

        while start_location >= 0:
            end_location = text.find(
                substr_end,
                start_location + substr_start_len,
                start_location + substr_start_len + limit + substr_end_len
            )
            if end_location >= 0:
                yield KnownFilth(
                    start_location,
                    end_location + substr_end_len,
                    text_orig[start_location:end_location + substr_end_len],
                    comparison_type=comparison_type,
                    detector_name=self.name,
                    document_name=document_name,
                    locale=self.locale,
                )
                next_search_start = end_location + substr_end_len
            else:
                next_search_start = start_location + substr_start_len

            start_location = text.find(substr_start, next_search_start)

    def iter_filth(
            self,
            text: str,
            document_name: Optional[str] = None
    ) -> Generator[KnownFilth, None, None]:
        """Yields discovered filth in the provided ``text``.

        :param text: The dirty text to clean.
        :type text: str
        :param document_name: The name of the document to clean.
        :type document_name: str, optional
        :return: An iterator to the discovered :class:`Filth`
        :rtype: Iterator[:class:`Filth`]
        """
        for pii_item in self._known_filth_items:
            # could also implement other types in here too
            ignore_case = pii_item.get('ignore_case', None)
            ignore_case = ignore_case if ignore_case is not None else False
            if 'match' in pii_item and 'match_end' in pii_item and pii_item['match_end'] is not None \
                    and len(pii_item['match_end']) > 0:
                yield from self._find_all_between(
                        text,
                        pii_item['match'],
                        pii_item['match_end'],
                        limit=int(pii_item.get('limit', 150) or 150),
                        comparison_type=pii_item.get('filth_type', None),
                        document_name=document_name,
                        ignore_case=ignore_case,
                )
            elif 'match' in pii_item:
                yield from self._find_all(
                        text,
                        pii_item['match'],
                        comparison_type=pii_item.get('filth_type', None),
                        document_name=document_name,
                        ignore_case=ignore_case,
                )
            else:
                raise ValueError(
                    "Unknown keys in predefined PII item: "
                    "{}".format(pii_item.keys())
                )
