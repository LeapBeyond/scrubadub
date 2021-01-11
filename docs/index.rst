.. _quick_start:

.. include:: ../README.rst

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
    :caption: Documentation

    Introduction <self>
    usage
    accuracy
    names
    addresses
    localization
    contributing
    changelog

.. toctree::
    :maxdepth: 2
    :name: api_toc
    :caption: API Reference

    api_scrubadub
    api_scrubadub_detectors
    api_scrubadub_filth
    api_scrubadub_post
    api_scrubadub_comparison


Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
