from .base import RegexFilth


class NameFilth(RegexFilth):

    @property
    def placeholder(self):
        return u'NAME'
