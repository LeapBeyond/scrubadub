import re

from .base import RegexFilth


class CredentialFilth(RegexFilth):
    type = 'credential'

    # specify how the username/password are replaced
    username_placeholder = 'USERNAME'
    password_placeholder = 'PASSWORD'

    # this regular expression searches for patterns like
    #     "username: root password: root"
    # that tend to occur very frequently in text. This does not currently catch
    # things like "username / password is root / root"
    regex = re.compile(r'''
        (username|login|u:)\s*:?\s*    # username might have : and whitespace
        (?P<username>[\w\-\.@+]*)      # capture the username for replacement
        \s+                            # some whitespace between
        (password|pw|p:)\s*:?\s*       # password might have : and whitespace
        (?P<password>.*)               # password can be anything until EOL
    ''', re.MULTILINE | re.VERBOSE | re.IGNORECASE)

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
