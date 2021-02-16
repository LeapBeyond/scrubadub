from typing import Sequence, Optional

from ...filth import Filth, MergedFilth
from ..base import PostProcessor


class FilthTypeReplacer(PostProcessor):
    name = 'filth_type_replacer'  # type: str

    @staticmethod
    def filth_label(filth, upper: bool = True, separator: Optional[str] = None) -> str:
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
            if filth_type == 'known':
                filth_comparison_type = getattr(f, 'comparison_type', None)
                if filth_comparison_type is not None:
                    filth_type += '_' + filth_comparison_type
            replacements.add(filth_type)

        # print(filths, replacements)
        label = separator.join(replacements)
        if upper:
            label = label.upper()
        return label

    def process_filth(self, filth_list: Sequence[Filth]) -> Sequence[Filth]:
        for filth_item in filth_list:
            filth_item.replacement_string = self.filth_label(filth_item)
        return filth_list


__all__ = ['FilthTypeReplacer']
