from typing import Sequence, Optional

from ...filth import Filth, MergedFilth, TaggedEvaluationFilth
from ..base import PostProcessor
from ... import utils


class FilthTypeReplacer(PostProcessor):
    name = 'filth_type_replacer'  # type: str

    # NOTE: this is not an efficient way to store this in memory. could
    # alternatively hash the type and text and do away with the overhead
    # bits of storing the tuple in the lookup
    lookup = utils.Lookup()

    def __init__(self, upper: bool = True, include_count: bool = False, separator: Optional[str] = None, **kawrgs):
        super(FilthTypeReplacer, self).__init__(**kawrgs)
        self.upper = upper
        self.include_count = include_count
        self.separator = separator

    @staticmethod
    def filth_label(filth, upper: bool = True, include_count: bool = False, separator: Optional[str] = None) -> str:
        if separator is None:
            separator = '+'
        filths = [filth]
        if isinstance(filth, MergedFilth):
            filths = filth.filths

        replacements = set()
        for f in filths:
            filth_type = getattr(f, 'type', None)
            if filth_type is None:
                continue
            if filth_type == TaggedEvaluationFilth.type:
                filth_comparison_type = getattr(f, 'comparison_type', None)
                if filth_comparison_type is not None:
                    filth_type += '_' + filth_comparison_type

            filth_type = filth_type.replace(' ', '_')

            if include_count:
                filth_type = '{}-{:d}'.format(
                    filth_type,
                    FilthTypeReplacer.lookup[(filth_type, f.text.lower())]
                )

            replacements.add(filth_type)

        # print(filths, replacements)
        label = separator.join(sorted(replacements))
        if upper:
            label = label.upper()
        return label

    def process_filth(self, filth_list: Sequence[Filth]) -> Sequence[Filth]:
        for filth_item in filth_list:
            filth_item.replacement_string = self.filth_label(
                filth=filth_item,
                upper=self.upper,
                include_count=self.include_count,
                separator=self.separator,
            )
        return filth_list


__all__ = ['FilthTypeReplacer']
