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

    >>> import scrubadub
    >>> scrubber = scrubadub.Scrubber()
    >>> scrubber.remove_detector('email')
    >>> text = u"contact Joe Duffy at joe@example.com"
    >>> scrubber.clean(text)
    u"contact {{NAME}} {{NAME}} at joe@example.com"


Customizing filth markers
-------------------------

By default, ``scrubadub`` uses mustache notation to signify what has been
removed from the dirty dirty text. This can be inconvenient in situations where
you want to display the information differently. You can customize the mustache
notation by changing the ``prefix`` and ``suffix`` in the
``scrubadub.filth.base.Filth`` object. For example, to bold all of the
resulting text in HTML, you might want to do this:

.. code:: pycon

    >>> import scrubadub
    >>> scrubadub.filth.base.Filth.prefix = u'<b>'
    >>> scrubadub.filth.base.Filth.suffix = u'</b>'
    >>> scrubber = scrubadub.Scrubber()
    >>> scrubber.remove_detector('email')
    >>> text = u"contact Joe Duffy at joe@example.com"
    >>> scrubber.clean(text)
    u"contact <b>NAME</b> <b>NAME</b> at <b>EMAIL</b>"


Adding a new type of filth
--------------------------

It is quite common for particular use cases of ``scrubadub`` to require
obfuscation of specific types of filth. If you run across something that is
very general, please :ref:`contribute it back <contributing>`! In the meantime,
you can always add your own ``Filth`` and ``Detectors`` like this:

.. code:: pycon

    >>> import scrubadub
    >>> class MyFilth(scrubadub.filth.base.Filth):
    >>>     type = 'mine'
    >>> class MyDetector(scrubadub.Detector.base.Detector):
    >>>     filth_cls = MyFilth
    >>>     def iter_filth(self, text):
    >>>        # do something here
    >>>        pass
    >>> scrubber = scrubadub.Scrubber()
    >>> scrubber.add_detector(MyDetector)
    >>> text = u"My stuff can be found there"
    >>> scrubber.clean(text)
    u"{{MINE}} can be found there."


Scanning for types of filth
---------------------------

Sometimes you don't want to replace the text, but instead see if there are any
types of filth in the text. In this case you can ``scan`` the text and get a 
list of filth that are found.

.. code:: pycon

    >>> import scrubadub
    >>> text = u"Contact Joe Duffy at joe@example.com. Website is http://www.example.com" 
    >>> scrubadub.scan(text)
    ['email', 'name', 'url']


Customizing the cleaned text
----------------------------

.. todo:: TKTK
