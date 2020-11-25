.. _api_scrubadub:

scrubadub
=========

There are several convenience functions to make using scrubadub quick and simple.
These functions either remove the Filth from the text (such as ``scrubadub.clean``) or
return a list of Filth objects that were found (such as ``scrubadub.list_filth``).
These functions either work on a single document in a string (such as ``scrubadub.clean``) or
work on a set of documents given in either a dictonary or list (such as ``scrubadub.clean_documents``).

scrubadub.clean
---------------

.. autofunction:: scrubadub.clean

scrubadub.clean_documents
-------------------------

.. autofunction:: scrubadub.clean_documents

scrubadub.list_filth
--------------------

.. autofunction:: scrubadub.list_filth

scrubadub.list_filth_documents
------------------------------

.. autofunction:: scrubadub.list_filth_documents


scrubadub.Scrubber
------------------

All of the ``Detector``'s are managed by the ``Scrubber``. The main job of the
``Scrubber`` is to handle situations in which the same section of text contains
different types of ``Filth``.

.. autoclass:: scrubadub.scrubbers.Scrubber
    :members:
    :undoc-members:
    :show-inheritance:

