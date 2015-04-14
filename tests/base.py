import inspect

import scrubadub


# this is a mixin class to make it easy to centralize a lot of the core
# functionality of the test suite
class BaseTestCase(object):

    def clean(self, text):
        return scrubadub.clean_with_placeholders(text)

    def compare_before_after(self, docstring=None):
        """This is a convenience method to make it easy to write tests without
        copy-pasting a lot of code. This method checks to make sure the BEFORE:
        text in the calling method's docstring matches the AFTER: text in the
        calling method's docstring.
        """
        # get the before and after outcomes from the docstring of the method
        # that calls compare_before_after
        if docstring is None:
            stack = inspect.stack()
            calling_function_name = stack[1][3]
            docstring = getattr(self, calling_function_name).__doc__
        before, after = docstring.split("BEFORE:")[1].split("AFTER:")
        before = unicode(before.strip())
        after = unicode(after.strip())

       # run a test to make sure the before string is the same as the after
       # string
        result = self.clean(before)
        self.assertEqual(
            result,
            after,
            '\nEXPECTED:\n"%s"\n\nBUT GOT THIS:\n"%s"'%(after, result),
        )
