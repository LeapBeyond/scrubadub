import inspect
import catalogue

from typing import Type, Optional, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from scrubadub.detectors import Detector

detector_catalogue = catalogue.create('scrubadub', 'detectors', entry_points=True)


def register_detector(detector: Type['Detector'], *, autoload: Optional[bool] = None) -> Type['Detector']:
    """Register a detector for use with the ``Scrubber`` class.

    You can use ``register_detector(NewDetector, autoload=True)`` after your detector definition to automatically
    register it with the ``Scrubber`` class so that it can be used to remove Filth.

    The argument ``autoload``decides whether a new ``Scrubber()`` instance should load this ``detector`` by default.

    .. code:: pycon

        >>> import scrubadub
        >>> class NewDetector(scrubadub.detectors.Detector):
        ...     pass
        >>> scrubadub.detectors.register_detector(NewDetector, autoload=False)
        <class 'scrubadub.detectors.catalogue.NewDetector'>

    :param detector: The ``Detector`` to register with the scrubadub detector configuration.
    :type detector: Detector class
    :param autoload: Whether to automatically load this ``Detector`` on ``Scrubber`` initialisation.
    :type autoload: Optional[bool]
    """
    if not inspect.isclass(detector):
        raise ValueError("detector should be a class, not an instance.")

    if autoload is not None:
        detector.autoload = autoload

    detector_catalogue.register(detector.name, func=detector)

    return detector


def remove_detector(detector: Union[Type['Detector'], str]):
    """Remove an already registered detector.

    .. code:: pycon

        >>> import scrubadub
        >>> class NewDetector(scrubadub.detectors.Detector):
        ...     pass
        >>> scrubadub.detectors.catalogue.register_detector(NewDetector, autoload=False)
        <class 'scrubadub.detectors.catalogue.NewDetector'>
        >>> scrubadub.detectors.catalogue.remove_detector(NewDetector)

    :param detector: The ``Detector`` to register with the scrubadub detector configuration.
    :type detector: Union[Type['PostProcessor'], str]
    :param autoload: Whether to automatically load this ``Detector`` on ``Scrubber`` initialisation.
    :type autoload: bool
    """
    if isinstance(detector, str):
        if detector in detector_catalogue:
            catalogue._remove((*detector_catalogue.namespace, detector))

    elif inspect.isclass(detector):
        if detector.name in detector_catalogue:
            catalogue._remove((*detector_catalogue.namespace, detector.name))

    else:
        raise ValueError("detector should be a class (not an instance) or a string.")
