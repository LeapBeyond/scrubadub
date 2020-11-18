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

.. autoclass:: scrubadub.post_processors.text_replacers.filth_type.FilthTypeReplacer
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: scrubadub.post_processors.text_replacers.hash.HashReplacer
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: scrubadub.post_processors.text_replacers.numeric.NumericReplacer
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: scrubadub.post_processors.text_replacers.prefix_suffix.PrefixSuffixReplacer
    :members:
    :undoc-members:
    :show-inheritance:
