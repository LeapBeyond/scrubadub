.. _quick_start:

*********
scrubadub
*********

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

.. image:: https://travis-ci.org/LeapBeyond/scrubadub.svg?branch=master
   :target: https://travis-ci.org/LeapBeyond/scrubadub
   :alt:  Build Status
.. image:: https://img.shields.io/pypi/v/scrubadub.svg
   :target: https://pypi.org/project/scrubadub/
   :alt:  Version
.. image:: https://img.shields.io/pypi/dm/scrubadub.svg
   :target: https://pypi.org/project/scrubadub/
   :alt:  Downloads
.. image:: https://coveralls.io/repos/github/LeapBeyond/scrubadub/badge.svg?branch=master
   :target: https://coveralls.io/r/LeapBeyond/scrubadub
   :alt:  Test Coverage
.. image:: https://readthedocs.org/projects/scrubadub/badge/?version=latest
   :target: https://readthedocs.org/projects/scrubadub/?badge=latest
   :alt:  Documentation Status


Quick start
-----------

Getting started with ``scrubadub`` is as easy as ``pip install scrubadub`` and
incorporating it into your python scripts like this:

.. code:: pycon

    >>> import scrubadub

    # John may be a cat, but he doesn't want other people to know it.
    >>> text = u"John is a cat"

    # Replace names with {{NAME-ID}} anonymous, but consistent IDs.
    >>> scrubadub.clean(text)
    u"{{NAME-0}} is a cat"

    >>> scrubadub.clean("John spoke with Doug.")
    u"{{NAME-0}} spoke with {{NAME-1}}."


There are many ways to tailor the behavior of ``scrubadub`` using
:ref:`different Detector and Filth classes <api>`. These
:ref:`advanced techniques <advanced_usage>` allow users to fine-tune the manner
in which ``scrubadub`` cleans dirty dirty text.


Installation
------------

To install scrubadub using pip, simply type::

    pip install scrubadub

This package requires at least python 3.5.
For python 2.7 support see v1.2.2 which is the last version with python 2.7 support.

There are a few python dependencies, which can be seen in the
`requirements file <https://github.com/LeapBeyond/scrubadub/blob/master/requirements/python>`__,
but these should be installed automatically when installing the package via pip.

.. TODO: talk about the fact that extra detectors can be installed here with pip install scrubadub[stanford_ner] in the future.

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


Contents
--------

.. toctree::
   :maxdepth: 2

   usage
   api
   accuracy
   contributing
   changelog


Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
