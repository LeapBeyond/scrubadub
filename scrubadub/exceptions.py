

# this is the base exception that is thrown by scrubadub to make it
# easy to suppress all Scrubadub exceptions
class ScrubadubException(Exception):

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
