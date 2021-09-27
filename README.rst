
.. NOTES FOR CREATING A RELEASE:
..
..   * bump the version number in scrubadub/__init__.py
..   * update docs/changelog.rst
..   * git push
..   * create a release https://github.com/LeapBeyond/scrubadub/releases
..      * This should trigger a github action to upload to pypi
..      * ReadTheDocs.io should see any changes and also rebuild the docs


*********
scrubadub
*********

Remove personally identifiable information from free text. Sometimes we have
additional metadata about the people we wish to anonymize. Other times we don't.
This package makes it easy to seamlessly scrub personal information from free
text, without compromising the privacy of the people we are trying to protect.

``scrubadub`` currently supports removing:

* Names
* Email addresses
* Addresses/Postal codes (US, GB, CA)
* Credit card numbers
* Dates of birth
* URLs
* Phone numbers
* Username and password combinations
* Skype/twitter usernames
* Social security numbers (US and GB national insurance numbers)
* Tax numbers (GB)
* Driving licence numbers (GB)

.. image:: https://img.shields.io/github/workflow/status/LeapBeyond/scrubadub/Python%20package/master
   :target: https://github.com/LeapBeyond/scrubadub/actions?query=workflow%3A%22Python+package%22+branch%3Amaster
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

    # My cat may be more tech-savvy than most, but he doesn't want other people to know it.
    >>> text = "My cat can be contacted on example@example.com, or 1800 555-5555"

    # Replaces the phone number and email addresse with anonymous IDs.
    >>> scrubadub.clean(text)
    'My cat can be contacted on {{EMAIL}}, or {{PHONE}}'


There are many ways to tailor the behavior of ``scrubadub`` using
`different Detectors and PostProcessors <https://scrubadub.readthedocs.io/en/stable/usage.html>`_.
Scrubadub is highly configurable and supports localisation for different languages and regions.

Installation
------------

To install scrubadub using pip, simply type::

    pip install scrubadub

There are several other packages that can optionally be installed to enable extra detectors.
These `scrubadub_address <https://github.com/LeapBeyond/scrubadub_address>`_, `scrubadub_spacy <https://github.com/LeapBeyond/scrubadub_spacy>`_ and `scrubadub_stanford <https://github.com/LeapBeyond/scrubadub_stanford>`_, see the relevant documentation (`address detector documentation <https://scrubadub.readthedocs.io/en/latest/addresses.html>`_ and `name detector documentation <https://scrubadub.readthedocs.io/en/latest/names.html>`_) for more info on these as they require additional dependencies.
This package requires at least python 3.6.
For python 2.7 or 3.5 support use v1.2.2 which is the last version with support for these versions.

New maintainers
---------------

`LeapBeyond <http://leapbeyond.ai/>`_ are excited to be supporting scrubadub with ongoing maintenance and development.
Thanks to all of the contributors who made this package a success, but especially `@deanmalmgren <https://github.com/deanmalmgren>`_, `IDEO <https://www.ideo.com/>`_ and `Datascope <https://datascopeanalytics.com/>`_.
