import unittest

from scrubadub import exceptions


class ExceptionsTestCase(unittest.TestCase):
    def test_render(self):
        exception = exceptions.ScrubadubException()
        exception.var = 'there'

        self.assertEquals(exception.render('test'), 'test')
        self.assertEquals(exception.render('url %(issues_url)s'), 'url ' + exception.issues_url)
        self.assertEquals(exception.render('hello %(var)s'), 'hello there')
