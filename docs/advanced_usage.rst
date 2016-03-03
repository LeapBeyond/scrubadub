.. _advanced_usage:

Advanced usage
==============

By default, ``scrubadub`` aggressively removes content from text that may
reveal personal identity, but there are certainly circumstances where you may
want to customize the behavior of ``scrubadub``. This section outlines a few of
these use cases. If you don't see your particular use case here, please take a
look :ref:`under the hood <under_the_hood>` and :ref:`contribute
<contributing>` it back to the documentation!


Suppressing a detector
----------------------

In some instances, you may wish to suppress a particular detector from removing
information. For example, if you have a specific reason to keep email addresses
in the resulting output, you can disable the email address cleaning like this:

.. code:: pycon

    import scrubadub
    scurbber = scrubadub.Scrubber()
    scrubber.remove_detector('email')
    >>> text = u"John's email address is cat@gmail.com"
    >>> text = scrubadub.clean(text)
    >>> text
    u"{{NAME}}'s email address is cat@gmail.com'"


Customizing cleaned text
------------------------

.. todo:: TKTK


Adding a new type of filth
--------------------------

.. todo:: TKTK


Customizing the cleaned text
----------------------------

.. todo:: TKTK
