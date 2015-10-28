
class LowerCaseSet(set):
    """Just like a set, excpet it makes sure that all elements are lower case
    strings.
    """

    def _cast_as_lower(self, x):
        if not isinstance(x, (str, unicode)):
            raise TypeError('LowerCaseSet only works with strings')
        return x.lower()

    def __init__(self, *elements):
        super(LowerCaseSet, self).__init__()
        if elements:
            self.update(*elements)

    def add(self, element):
        super(LowerCaseSet, self).add(self._cast_as_lower(element))

    def update(self, elements):
        for element in elements:
            self.add(element)

    def __contains__(self, element):
        return super(LowerCaseSet, self).__contains__(
            self._cast_as_lower(element)
        )
