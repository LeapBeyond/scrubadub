"""scrubadub has some very conservative defaults (high recall) for identifying
filth. One of the key ways in which scrubadub can be customized is in improving
the precision of filth detection.

For example, if a user knows that the word 'iPhone' is not a person's name, but
a product, then a user should be able to easily adapt how scrubadub identifies
names.
"""

import scrubadub

# fine-tune how scrubadub detects names and omit product names
# https://github.com/deanmalmgren/scrubadub/issues/6
class MyNameDetector(scrubadub.detectors.TextBlobNameDetector):
    def iter_filth(self, text):
        for filth in super(MyNameDetector, self).iter_filth(text):
            if filth != "iPhone":
                yield filth

# instantiate a scrubber and change the name detector to use our custom class
scrubber = scrubadub.Scrubber()
scrubber.detectors['name'] = MyNameDetector()

# these methods have identical on a Scrubber object should have identical
# behavior to the scrubadub.clean convenience function
clean_text = scrubber.clean(text)
clean_text = scrubber.clean(text, replace_with="placeholder")
clean_text = scrubber.clean(text, replace_with="surrogate")
clean_text = scrubber.clean(text, replace_with="identifier", lookup=lookup)
