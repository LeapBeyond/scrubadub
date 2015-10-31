"""scrubadub uses {{}} notation by default to identify filth, but a user may
prefer to fine-tune how the filth is removed.

For example, if the input text is html, then a user may want the filth to be
included in a <span> tag that has a particular class on it to make it easy to
style these things.

Another example is a situation when a user wants to retain the domain name on a
URL but not the path.
"""

import scrubadub

# fine tune the prefix and suffix for all scrubadub objects. because this is
# changing a class attribute on the base class, this should propagate to all
# filth
scrubadub.filth.Filth.prefix = '<span class="scrubadub filth">'
scrubadub.filth.Filth.suffix = '</span>'

# these methods should now all have that prefix and suffix
clean_text = scrubadub.clean(text)
clean_text = scrubadub.clean(text, replace_with="placeholder")
clean_text = scrubadub.clean(text, replace_with="surrogate")
clean_text = scrubadub.clean(text, replace_with="identifier", lookup=lookup)

# and so should these
scrubber = scrubadub.Scrubber()
clean_text = scrubber.clean(text)
clean_text = scrubber.clean(text, replace_with="placeholder")
clean_text = scrubber.clean(text, replace_with="surrogate")
clean_text = scrubber.clean(text, replace_with="identifier", lookup=lookup)


# reconfigure back to the old prefix and suffix combination and now keep the
# domain on UrlFilth
scrubadub.filth.Filth.prefix = '{{'
scrubadub.filth.Filth.suffix = '}}'
scrubadub.filth.UrlFilth.keep_domain = True

# these methods should now all have that prefix and suffix
clean_text = scrubadub.clean(text)
clean_text = scrubadub.clean(text, replace_with="placeholder")
clean_text = scrubadub.clean(text, replace_with="surrogate")
clean_text = scrubadub.clean(text, replace_with="identifier", lookup=lookup)
