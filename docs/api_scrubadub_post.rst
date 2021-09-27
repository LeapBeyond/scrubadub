.. _api_scrubadub_post:

scrubadub.post_processors
-------------------------

``PostProcessor``\ s generally can be used to process the detected ``Filth``
objects and make changes to them.

These are a new addition to scrubadub and at the moment only simple ones
exist that alter the replacement string.

.. autoclass:: scrubadub.post_processors.base.PostProcessor
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: scrubadub.post_processors.filth_replacer.FilthReplacer
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: scrubadub.post_processors.prefix_suffix.PrefixSuffixReplacer
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: scrubadub.post_processors.remover.FilthRemover
    :members:
    :undoc-members:
    :show-inheritance:


Catalogue functions
-------------------

.. _scrubadub.post_processors.register_post_processor:

scrubadub.post_processors.register_post_processor
-------------------------------------------------

.. autofunction:: scrubadub.post_processors.register_post_processor

.. _scrubadub.post_processors.remove_post_processor:

scrubadub.post_processors.remove_post_processor
-----------------------------------------------

.. autofunction:: scrubadub.post_processors.remove_post_processor

