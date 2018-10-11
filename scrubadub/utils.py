import pickle
import uuid
import hashlib

try:
    unicode
except NameError:
    basestring = str  # Compatibility for Python 2 and 3


class CanonicalStringSet(set):
    """Just like a set, except it makes sure that all elements are lower case
    strings.
    """

    def _cast_as_lower(self, x):
        if not isinstance(x, basestring):
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


class Lookup(object):
    """The Lookup object is used to create an in-memory reference table to
    create unique identifiers for ``Filth`` that is encountered.
    """

    def __init__(self):
        self.table = {}

    def __getitem__(self, key):
        try:
            return self.table[key]
        except KeyError:
            self.table[key] = len(self.table)
            return self.table[key]


class PersistentLookup(Lookup):
    """PersistentLookup persists the reference table for ``Filth``
    identifiers so that they remain consistent across runs.

    For security the PersistentLookup is slower since it must obfuscate
    the keys so they cannot be reversed.
    """

    def __init__(self, path):
        self.path = path
        self.salt = uuid.uuid4().bytes
        return super().__init__()

    def obfuscate_key(self, key):
        key = (key[0],
               hashlib.sha1(key[1].encode('utf-8') + self.salt).hexdigest())
        return key

    def __getitem__(self, key):
        return super().__getitem__(self.obfuscate_key(key))

    def save(self):
        with open(self.path, 'wb') as f:
            pickle.dump(self, f)
