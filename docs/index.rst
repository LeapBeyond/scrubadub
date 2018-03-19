
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
* Social security numbers


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
    >>> scrubadub.clean(text)
    u"{{NAME}} is a cat"

    # Replace names with {{NAME-ID}} anonymous, but consistent IDs.
    >>> scrubadub.clean(text, replace_with='identifier')
    u"{{NAME-0}} is a cat"
    >>> scrubadub.clean("John spoke with Doug.", replace_with='identifier')
    u"{{NAME-0}} spoke with {{NAME-1}}."

..    # Replace names with random, gender-consistent names
    >>> scrubadub.clean(text, replace_with='surrogate')
    u"Billy is a cat"


There are many ways to tailor the behavior of ``scrubadub`` using
:ref:`different Detector and Filth classes <under_the_hood>`. These
:ref:`advanced techniques <advanced_usage>` allow users to fine-tune the manner
in which ``scrubadub`` cleans dirty dirty text.


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
   under_the_hood
   contributing
   changelog


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
