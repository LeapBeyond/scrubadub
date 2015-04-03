
# convenient imports
from .scrubbers import Scrubber


__version__ = VERSION = "0.0.1"


def clean(text):
    scrubber = Scrubber()
    return scrubber.clean(text)
