"""This is the basic usage of the scrubadub module. It exposes three different
methods for obfuscating personally identifiable information and uses high
recall methods for identifying filth. Precision can be improved by further
customization.
"""

import scrubadub

# this should have very smart defaults, with high recall and relatively low
# precision. the placeholder method is default and uses {{}} notation to
# signify when text has been obfuscated
clean_text = scrubadub.clean(text)
clean_text = scrubadub.clean(text, replace_with="placeholder")

# the surrogate replacement method makes it easy to replace phone numbers with
# fake phone numbers, for example. this makes it easy to read the content
clean_text = scrubadub.clean(text, replace_with="surrogate")

# the identifier replacement method replaces the personal information
# associated with each person in lookup with the same unique id to make it easy
# to detect the same person across document records.
clean_text = scrubadub.clean(text, replace_with="identifier", lookup=lookup)
