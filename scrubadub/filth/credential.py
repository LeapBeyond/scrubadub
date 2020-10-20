from .base import Filth
from .. import exceptions


class CredentialFilth(Filth):
    type = 'credential'

    # specify how the username/password are replaced
    username_placeholder = 'USERNAME'
    password_placeholder = 'PASSWORD'

    @property
    def placeholder(self):
        ubeg, uend = self.match.span('username')
        pbeg, pend = self.match.span('password')
        return (
            self.match.string[self.match.start():ubeg] +
            self.prefix + self.username_placeholder + self.suffix +
            self.match.string[uend:pbeg] +
            self.prefix + self.password_placeholder + self.suffix
        )

    # override the replace_with method for credentials because the
    # prefix/suffix components are mixed into the placeholder
    def replace_with(self, replace_with='placeholder', **kwargs):
        if replace_with == 'placeholder':
            return self.placeholder
        else:
            raise exceptions.InvalidReplaceWith(replace_with)
