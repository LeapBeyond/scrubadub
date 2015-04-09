.. _advanced_usage:

Advanced usage
==============

By default, ``scrubadub`` aggressively removes content from text that may reveal
personal identity, but there are certainly circumstances where such omissions
are (i) not necessary and (ii) detrimental to downstream analysis. ``scrubadub``
allows users to fine-tune the manner in which content is deidentified using the
specific methods in the  ``scrubadub.scrubbers.Scrubber`` class.

.. autoclass:: scrubadub.scrubbers.Scrubber
    :members:
