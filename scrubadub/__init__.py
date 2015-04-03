
# convenient imports
from .scrubbers import Scrubber


def clean(text):
    scrubber = Scrubber()
    return scrubber.clean(text)
