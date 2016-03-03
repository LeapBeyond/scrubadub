from .. import exceptions
from .. import utils


class Filth(object):
    """This is the base class for all ``Filth`` that is detected in dirty dirty
    text.
    """

    # this allows people to customize the output, especially for placeholder
    # text and identifier replacements
    prefix = u'{{'
    suffix = u'}}'

    # the `type` is used when filths are merged to come up with a sane label
    type = None

    # the `lookup` is used to keep track of all of the diffent types of filth
    # that are encountered across all `Filth` types.
    lookup = utils.Lookup()

    def __init__(self, beg=0, end=0, text=u''):
        self.beg = beg
        self.end = end
        self.text = text

    @property
    def placeholder(self):
        return self.type.upper()

    @property
    def identifier(self):
        # NOTE: this is not an efficient way to store this in memory. could
        # alternatively hash the type and text and do away with the overhead
        # bits of storing the tuple in the lookup
        i = self.lookup[(self.type, self.text.lower())]
        return u'%s-%d' % (self.placeholder, i)

    def replace_with(self, replace_with='placeholder', **kwargs):
        if replace_with == 'placeholder':
            return self.prefix + self.placeholder + self.suffix
        # elif replace_with == 'surrogate':
        #     raise NotImplementedError
        elif replace_with == 'identifier':
            return self.prefix + self.identifier + self.suffix
        else:
            raise exceptions.InvalidReplaceWith(replace_with)

    def merge(self, other_filth):
        return MergedFilth(self, other_filth)


class MergedFilth(Filth):
    """This class takes care of merging different types of filth"""

    def __init__(self, a_filth, b_filth):
        super(MergedFilth, self).__init__(
            beg=a_filth.beg,
            end=a_filth.end,
            text=a_filth.text,
        )
        self.filths = [a_filth]
        self._update_content(b_filth)

    def _update_content(self, other_filth):
        """this updates the bounds, text and placeholder for the merged
        filth
        """
        if self.end < other_filth.beg or other_filth.end < self.beg:
            raise exceptions.FilthMergeError(
                "a_filth goes from [%s, %s) and b_filth goes from [%s, %s)" % (
                    self.beg, self.end, other_filth.beg, other_filth.end
                ))

        # get the text over lap correct
        if self.beg < other_filth.beg:
            first = self
            second = other_filth
        else:
            second = self
            first = other_filth
        end_offset = second.end - first.end
        if end_offset > 0:
            self.text = first.text + second.text[-end_offset:]

        # update the beg/end strings
        self.beg = min(self.beg, other_filth.beg)
        self.end = max(self.end, other_filth.end)
        if self.end - self.beg != len(self.text):
            raise exceptions.FilthMergeError("text length isn't consistent")

        # update the placeholder
        self.filths.append(other_filth)
        self._placeholder = '+'.join([filth.type for filth in self.filths])

    @property
    def placeholder(self):
        return self._placeholder.upper()

    def merge(self, other_filth):
        """Be smart about merging filth in this case to avoid nesting merged
        filths.
        """
        self._update_content(other_filth)
        return self


class RegexFilth(Filth):
    """Convenience class for instantiating a ``Filth`` object from a regular
    expression match
    """

    # The regex is stored on the RegexFilth so you can use groups in the
    # regular expression to properly configure the placeholder
    regex = None

    def __init__(self, match):
        self.match = match
        super(RegexFilth, self).__init__(
            beg=match.start(),
            end=match.end(),
            text=match.string[match.start():match.end()],
        )
