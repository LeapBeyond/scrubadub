from .base import RegexFilth

class EmailFilth(RegexFilth):
    def __init__(self, *args, **kwargs):
        super(EmailFilth, self).__init__(*args, **kwargs)
        self.placeholder = u'EMAIL'
