

# this is the base exception that is thrown by scrubadub to make it
# easy to suppress all Scrubadub exceptions
class ScrubadubException(Exception):

    def __init__(self, *args, **kwargs):
        self.issues_url = 'http://github.com/deanmalmgren/scrubadub/issues'

    def render(self, msg):
        return msg % vars(self)


class UnicodeRequired(ScrubadubException):
    """Scrubadub requires unicode. Throw a useful error to lead users to
    the promised land.
    """

    def __str__(self):
        return self.render((
            'scrubadub works best with unicode.\n'
            'Frustrated by unicode?\n'
            'Yeah, me too.\n'
            'But unicode sandwiches are awesome.\n'
            'http://bit.ly/unipain @nedbat\n'
        ))


class UnexpectedFilth(ScrubadubException):
    pass


class FilthMergeError(ScrubadubException):
    pass


class InvalidReplaceWith(ScrubadubException):

    def __init__(self, replace_with):
        super(InvalidReplaceWith, self).__init__()
        self.replace_with = replace_with

    def __str__(self):
        return self.render((
            'Invalid replace_with parameter %(replace_with)s. Can only use '
            '`placeholder` for the time being. If you have other ideas for '
            'replace_with functionality, please make a suggestion at '
            '%(issues_url)s'
        ))
