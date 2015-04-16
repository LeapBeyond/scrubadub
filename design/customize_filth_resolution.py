"""scrubadub ships with a very good method for resolving conflicts between
overlapping pieces of filth. There may be cases where it is necessary to
resolve these conflicts in a customized way to account for additional
information that someone might have.

For example, a user may preferentially want to remove any hint of a name from
text.
"""

import scrubadub
from scrubadub.filth import NameFilth

class MyScrubber(scrubadub.Scrubber):
    def resolve_conflicting_filth(self, *filths):
        for filth in filths:
            if isinstance(filth, NameFilth):
                return filth
        return super(MyScrubber, self).resolve_conflicting_filth(*filths)

# these methods on a Scrubber object should have identical behavior to the
# scrubadub.clean convenience function
scrubber.clean(text)
scrubber.clean(text, replace_with="placeholder")
scrubber.clean(text, replace_with="identifier")
scrubber.clean(text, replace_with="surrogate")
