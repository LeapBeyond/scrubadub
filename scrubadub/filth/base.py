from .. import exceptions


class Filth(object):
    """This is the base class for all ``Filth`` that is detected in dirty dirty
    text.
    """

    prefix = u'{{'
    suffix = u'}}'

    def __init__(self, beg=0, end=0, text=u''):
        self.beg = beg
        self.end = end
        self.text = text

    @property
    def placeholder(self):
        return u''

    def replace_with(self, replace_with='placeholder', **kwargs):
        if replace_with == 'placeholder':
            return self.prefix + self.placeholder + self.suffix
        # elif replace_with == 'surrogate':
        #     raise NotImplementedError
        # elif replace_with == 'identifier':
        #     raise NotImplementedError
        else:
            raise exceptions.InvalidReplaceWith(replace_with)

    def merge(self, other_filth):
        """Merge two filths that are overlapping"""
        if self.end < other_filth.beg or other_filth.end < self.beg:
            raise exceptions.FilthMergeError(
                "a_filth goes from [%s, %s) and b_filth goes from [%s, %s)" % (
                self.beg, self.end, other_filth.beg, other_filth.end
            ))

        # TODO: fix placeholder b.s.
        # self.placeholder += '+' + other_filth.placeholder

        if self.beg < other_filth.beg:
            first = self
            second = other_filth
        else:
            second = self
            first = other_filth
        end_offset = second.end - first.end
        if end_offset > 0:
            self.text = first.text + second.text[-end_offset:]

        self.beg = min(self.beg, other_filth.beg)
        self.end = max(self.end, other_filth.end)
        if self.end - self.beg != len(self.text):
            raise exceptions.FilthMergeError("text length isn't consistent")
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
