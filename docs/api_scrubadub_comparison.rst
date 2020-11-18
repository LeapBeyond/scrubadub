.. _api_scrubadub_comparison:


scrubadub.comparison
====================

Filth objects are responsible for marking particular sections of text as
containing that type of filth. It is also responsible for knowing how it should
be cleaned. Every type of ``Filth`` inherits from ``scrubadub.filth.base.Filth``.

.. autofunction:: scrubadub.comparison.get_filth_classification_report

.. autofunction:: scrubadub.comparison.get_filth_dataframe

.. autofunction:: scrubadub.comparison.make_fake_document
