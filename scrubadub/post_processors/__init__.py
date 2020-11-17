import sys
from typing import Dict, Type

if sys.version_info >= (3, 8):
    from typing import TypedDict  # pylint: disable=no-name-in-module
else:
    from typing_extensions import TypedDict

from .base import PostProcessor
from .text_replacers.filth_type import FilthTypeReplacer
from .text_replacers.hash import HashReplacer
from .text_replacers.numeric import NumericReplacer
from .text_replacers.prefix_suffix import PrefixSuffixReplacer

PostProcessorConfigurationItem = TypedDict(
    'PostProcessorConfigurationItem',
    {'post_processor': Type[PostProcessor], 'autoload': bool, 'index': int}
)

post_processor_configuration = {
    # PostProcessors that are not automatically loaded by scrubadub
    NumericReplacer.name: {'post_processor': NumericReplacer, 'autoload': False, 'index': 0},
    PrefixSuffixReplacer.name: {'post_processor': PrefixSuffixReplacer, 'autoload': False, 'index': 1},
    FilthTypeReplacer.name: {'post_processor': FilthTypeReplacer, 'autoload': False, 'index': 0},
    HashReplacer.name: {'post_processor': HashReplacer, 'autoload': False, 'index': 0},
}  # type: Dict[str, PostProcessorConfigurationItem]


def register_post_processor(post_processor: Type[PostProcessor], autoload: bool = False, index: int = 0):
    """Register a PostProcessor for use with the ``Scrubber`` class.

    This is used when you don't want to have to import a detector by default.
    It may be useful for certain detectors with large or unusual dependencies, which you may not always want to import.
    In this case you can use ``register_detector(NewDetector, autoload=True)`` after your detector definition so that
    if the file is imported it wil be automatically registered.
    This will mean that you don't need to import the ``NewDetector`` in this file and so it's dependencies won't need
    to be installed just to import this package.

    The argument ``autoload`` sets if a new ``Scrubber()`` instance should load this ``Detector`` by default.

    :param post_processor: The ``PostProcessor`` to register with the scrubadub post-processor configuration.
    :type post_processor: PostProcessor class
    :param autoload: Whether to automatically load this ``Detector`` on ``Scrubber`` initialisation.
    :type autoload: bool
    :param index: The location/index in which this ``PostProcessor`` should be added.
    :type index: int
    """
    post_processor_configuration[post_processor.name] = {
        'post_processor': post_processor,
        'autoload': autoload,
        'index': index,
    }
    current_module = __import__(__name__)
    setattr(current_module.post_processors, post_processor.__name__, post_processor)
