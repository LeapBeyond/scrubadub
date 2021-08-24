import inspect
import catalogue

from typing import Type, Optional, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from scrubadub.post_processors import PostProcessor

post_processor_catalogue = catalogue.create('scrubadub', 'post_processors', entry_points=True)


def register_post_processor(post_processor: Type['PostProcessor'], autoload: Optional[bool] = None,
                            index: Optional[int] = None) -> None:
    """Register a PostProcessor for use with the ``Scrubber`` class.

    You can use ``register_post_processor(NewPostProcessor)`` after your post-processor definition to automatically
    register it with the ``Scrubber`` class so that it can be used to process Filth.

    The argument ``autoload`` sets if a new ``Scrubber()`` instance should load this ``PostProcessor`` by default.

    :param post_processor: The ``PostProcessor`` to register with the scrubadub post-processor configuration.
    :type post_processor: PostProcessor class
    :param autoload: Whether to automatically load this ``Detector`` on ``Scrubber`` initialisation.
    :type autoload: bool
    :param index: The location/index in which this ``PostProcessor`` should be added.
    :type index: int
    """
    if not inspect.isclass(post_processor):
        raise ValueError("post_processor should be a class, not an instance.")

    if autoload is not None:
        post_processor.autoload = autoload

    if index is not None:
        post_processor.index = index

    post_processor_catalogue.register(post_processor.name, func=post_processor)


def remove_post_processor(post_processor: Union[Type['PostProcessor'], str]) -> None:
    """Remove an already registered post-processor.

    :param post_processor: The ``PostProcessor`` to register with the scrubadub post-processor configuration.
    :type post_processor: Union[Type['PostProcessor'], str]
    """
    if isinstance(post_processor, str):
        if post_processor in post_processor_catalogue:
            catalogue._remove((*post_processor_catalogue.namespace, post_processor))

    elif inspect.isclass(post_processor):
        if post_processor.name in post_processor_catalogue:
            catalogue._remove((*post_processor_catalogue.namespace, post_processor.name))

    else:
        raise ValueError("post-processor should be a class (not an instance) or a string.")
