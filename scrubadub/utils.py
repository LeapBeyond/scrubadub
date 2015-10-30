
class CanonicalStringSet(set):
    """Just like a set, except it makes sure that all elements are lower case
    strings.
    """

    def _cast_as_lower(self, x):
        if not isinstance(x, (str, unicode)):
            raise TypeError('CanonicalStringSet only works with strings')
        return x.lower()

    def __init__(self, *elements):
        super(CanonicalStringSet, self).__init__()
        if elements:
            self.update(*elements)

    def __contains__(self, element):
        return super(CanonicalStringSet, self).__contains__(
            self._cast_as_lower(element)
        )

    def add(self, element):
        return super(CanonicalStringSet, self).add(
            self._cast_as_lower(element)
        )

    def update(self, elements):
        for element in elements:
            self.add(element)

    def remove(self, element):
        return super(CanonicalStringSet, self).remove(
            self._cast_as_lower(element)
        )

    def discard(self, element):
        return super(CanonicalStringSet, self).discard(
            self._cast_as_lower(element)
        )
