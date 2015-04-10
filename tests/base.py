import scrubadub


# this is a mixin class to make it easy to centralize a lot of the core
# functionality of the test suite
class BaseTestCase(object):

    def clean(self, text):
        return scrubadub.clean_with_placeholders(text)
