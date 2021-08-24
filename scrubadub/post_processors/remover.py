from typing import Sequence

from scrubadub.post_processors.catalogue import register_post_processor
from scrubadub.filth import Filth
from scrubadub.post_processors.base import PostProcessor


class FilthRemover(PostProcessor):
    """Removes all found filth from the original document.

    >>> import scrubadub
    >>> scrubber = scrubadub.Scrubber(post_processor_list=[
    ...     scrubadub.post_processors.FilthRemover(),
    ... ])
    >>> scrubber.clean("Contact me at 522-368-8530 or hernandezjenna@example.com")
    'Contact me at  or '

    """
    name = 'filth_remover'  # type: str
    autoload = False
    index = 0

    def process_filth(self, filth_list: Sequence[Filth]) -> Sequence[Filth]:
        """Processes the filth to remove the filth

        :param filth_list: The text to be hashed
        :type filth_list: Sequence[Filth]
        :return: The processed filths
        :rtype: Sequence[Filth]
        """
        for filth_item in filth_list:
            filth_item.replacement_string = ''
        return filth_list


register_post_processor(FilthRemover)

__all__ = ['FilthRemover']
