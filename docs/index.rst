.. warning::

    This package is a work in progress and is not yet available on pypi. This
    documentation should be considered more of a design document for what
    scrubadub will do someday rather than a specification of what it can do
    today.


scrubadub
================================

Remove personally identifiable information from free text. Sometimes we have
additional metadata about the people we wish to anonymize. Other times we don't.
This package makes it easy to seamlessly scrub personal information from free
text, without comprimising the privacy of the people we are trying to protect.

``scrubadub`` currently supports removing:

* Names (proper nouns) via `textblob <http://textblob.readthedocs.org/en/dev/>`_
* Email addresses
* URLs
* Phone numbers via `phonenumbers
  <https://github.com/daviddrysdale/python-phonenumbers>`_
* username / password combinations
* Skype usernames

Quick start
-----------

Getting started with ``scrubadub`` is as easy as ``pip install scrubadub`` and
incorporating it into your python scripts like this:

.. code:: pycon

    >>> import scrubadub

    # John may be a cat, but he doesn't want other people to know it.
    >>> text = u"John is a cat"

    # Replace names with {{NAME}} placeholder. This is the scrubadub default
    # because it maximally omits any information about people.
    >>> placeholder_text = scrubadub.clean_with_placeholders(text)
    >>> placeholder_text
    u"{{NAME}} is a cat"

..    # Replace names with {{NAME-ID}} anonymous, but consistent IDs.
    >>> identifier_text = scrubadub.clean_with_identifiers(text)
    >>> identifier_text
    u"{{NAME-1287}} is a cat"

..    # Replace names with random, gender-consistent names
    >>> surrogate_text = scrubadub.clean_with_surrogates(text)
    >>> surrogate_text
    u"Billy is a cat"

..    # For more fine-grained control, you can subclass Scrubber and adapt your
    # approach for your particular use case. For example, if you have a specific
    # reason to keep email addresses in the resulting output, you can disable
    # the email address cleaning like this:
    >>> class NoEmailScrubber(scrubadub.Scrubber):
    ...     def clean_email_addresses(self, text):
    ...         return text
    ...
    >>> text = u"John's email address is cat@gmail.com"
    >>> text = scrubadub.clean_with_placeholders(text, cls=NoEmailScrubber)
    >>> text
    u"{{NAME}}'s email address is cat@gmail.com'"

As a python package, ``scrubadub`` also has several more :ref:`advanced features <advanced_usage>` to
allow users to fine-tune the manner in which ``scrubadub`` cleans dirty dirty
text.


Related work
------------

``scrubadub`` isn't the first package to attempt to remove personally
identifiable information from free text. There are a handful of other
projects out there that have very similar aims and which provide some
inspiration for how ``scrubadub`` should work.

-  `MITRE <http://mist-deid.sourceforge.net/>`__ gives the ability to
   replace names with a placeholder like ``[NAME]`` or alternatively
   replace names with fake names. last release in 8/2014. not on github.
   unclear what language although it looks like python. it is clear that
   the documentation sucks and is primarily intended for academic
   audiences (docs are in papers).

-  `physionet has a few deidentification
   packages <http://www.physionet.org/physiotools/software-index.shtml#deid>`__
   that look pretty decent but are both written in perl and require
   advance knowledge of what you are trying to replace. Intended for
   HIPAA regulations. In particular,
   `deid <http://www.physionet.org/physiotools/deid/>`__ has some good
   lists of names that might be useful in spite of the fact it has 5k+
   lines of gross perl.

.. |Build Status| image:: https://travis-ci.org/datascopeanalytics/scrubadub.svg?branch=master
   :target: https://travis-ci.org/datascopeanalytics/scrubadub
.. |Coverage Status| image:: https://coveralls.io/repos/datascopeanalytics/scrubadub/badge.svg
   :target: https://coveralls.io/r/datascopeanalytics/scrubadub


Contents:

.. toctree::
   :maxdepth: 2

   advanced_usage
   contributing
   changelog


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
