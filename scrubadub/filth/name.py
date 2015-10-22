from .base import RegexFilth

class NameFilth(RegexFilth):
    def __init__(self, *args, **kwargs):
        super(NameFilth, self).__init__(*args, **kwargs)
        self.placeholder = u'NAME'
