import typing

from .base import Detector
from ..filth.known import KnownFilth


class KnownFilthDetector(Detector):
    """Use some predefined phrases to label the text.

    This is useful if you have found that some particular
    type of PII occurs regularly or you want to compare
    scrubadub with already selected PII.
    """

    filth_cls = KnownFilth

    def __init__(self, predefined_pii: typing.Optional[typing.List[typing.Dict[str, str]]] = None):
        super().__init__()
        if predefined_pii is None:
            predefined_pii = []
        self._predefined_pii = predefined_pii

    @staticmethod
    def _find_all(
            text,
            substr,
            comparison_type: typing.Optional[str] = None,
    ) -> typing.Generator[KnownFilth, None, None]:
        """Yield filth for each match to substr in text."""
        substr_len = len(substr)
        start_location = text.find(substr)

        while start_location >= 0:
            yield KnownFilth(
                start_location,
                start_location + substr_len,
                text[start_location:start_location + substr_len],
                comparison_type=comparison_type,
            )
            start_location = text.find(
                substr,
                start_location + substr_len
            )

    @staticmethod
    def _find_all_between(
            text: str,
            substr_start: str,
            substr_end: str,
            limit: int = 150,
            comparison_type: typing.Optional[str] = None,
    ) -> typing.Generator[KnownFilth, None, None]:
        """Yield filth for text between (and including)
        substr_start and substr_end, but only if the text
        between the two is less than limit characters.
        """
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
                    text[start_location:end_location + substr_end_len],
                    comparison_type=comparison_type,
                )
                next_search_start = end_location + substr_end_len
            else:
                next_search_start = start_location + substr_start_len

            start_location = text.find(substr_start, next_search_start)

    def iter_filth(
            self,
            text: str
    ) -> typing.Generator[KnownFilth, None, None]:
        """Iterate over the predefined PII list and yield
        filth instances."""
        for pii_item in self._predefined_pii:
            # could also implement other types in here too
            if 'match' in pii_item:
                for found_item in self._find_all(
                        text,
                        pii_item['match'],
                        comparison_type=pii_item.get('comparison_type', None)
                ):
                    yield found_item
            elif 'start' in pii_item and 'end' in pii_item:
                for found_item in self._find_all_between(
                    text,
                    pii_item['start'],
                    pii_item['end'],
                    limit=pii_item.get('limit', 150),
                    comparison_type=pii_item.get('comparison_type', None)
                ):
                    yield found_item
            else:
                raise ValueError(
                    "Unknown keys in predefined PII item: "
                    "{}".format(pii_item.keys())
                )
