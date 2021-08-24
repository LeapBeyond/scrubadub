from typing import Optional, Sequence

from scrubadub.filth import Filth
from scrubadub.post_processors.catalogue import register_post_processor
from scrubadub.post_processors.base import PostProcessor


class PrefixSuffixReplacer(PostProcessor):
    """Add a prefix and/or suffix to the Filth's replacement string.

    >>> import scrubadub
    >>> scrubber = scrubadub.Scrubber(post_processor_list=[
    ...     scrubadub.post_processors.FilthReplacer(),
    ... ])
    >>> scrubber.clean("Contact me at 522-368-8530 or hernandezjenna@example.com")
    'Contact me at PHONE or EMAIL'
    >>> scrubber = scrubadub.Scrubber(post_processor_list=[
    ...     scrubadub.post_processors.FilthReplacer(),
    ...     scrubadub.post_processors.PrefixSuffixReplacer(prefix='{{', suffix='}}'),
    ... ])
    >>> scrubber.clean("Contact me at 522-368-8530 or hernandezjenna@example.com")
    'Contact me at {{PHONE}} or {{EMAIL}}'
    >>> scrubber = scrubadub.Scrubber(post_processor_list=[
    ...     scrubadub.post_processors.FilthReplacer(),
    ...     scrubadub.post_processors.PrefixSuffixReplacer(prefix='<b>', suffix='</b>'),
    ... ])
    >>> scrubber.clean("Contact me at 522-368-8530 or hernandezjenna@example.com")
    'Contact me at <b>PHONE</b> or <b>EMAIL</b>'

    """
    name = 'prefix_suffix_replacer'  # type: str
    autoload = False
    index = 1

    def __init__(self, prefix: Optional[str] = '{{', suffix: Optional[str] = '}}', name: Optional[str] = None):
        super(PrefixSuffixReplacer, self).__init__(name=name)

        self.prefix = prefix
        self.suffix = suffix

    def process_filth(self, filth_list: Sequence[Filth]) -> Sequence[Filth]:
        """Processes the filth to add prefixes and suffixes to the replacement text

        :param filth_list: The text to be hashed
        :type filth_list: Sequence[Filth]
        :return: The processed filths
        :rtype: Sequence[Filth]
        """
        for filth_item in filth_list:
            if filth_item.replacement_string is None:
                filth_item.replacement_string = filth_item.type.upper()

            if self.prefix is not None and self.suffix is not None:
                filth_item.replacement_string = self.prefix + filth_item.replacement_string + self.suffix
            elif self.prefix is not None:
                filth_item.replacement_string = self.prefix + filth_item.replacement_string
            elif self.suffix is not None:
                filth_item.replacement_string = filth_item.replacement_string + self.suffix

        return filth_list


register_post_processor(PrefixSuffixReplacer)

__all__ = ['PrefixSuffixReplacer']
