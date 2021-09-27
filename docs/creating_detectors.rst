.. _creating_detectors:

Creating New Detectors
======================

To create a new detector you can simply create a new class that inherits from :ref:`scrubadub.detectors.Detector` and
define the ``iter_filth(self, text, document_name=None)`` function, which should yield ``Filth`` instances.
If you are finding a new type of filth, perhaps you even want to define your own type of ``Filth`` otherwise you can
reuse any of the existing ``Filth``\ -types available in ``scrubadub.filth``.

In the example below we are preventing others finding out what types of fruit we grow, and so we are removing all
fruit from the text.

.. code:: pycon

    >>> import scrubadub

    >>> class FruitFilth(scrubadub.filth.Filth):
    ...     type = 'fruit'

    >>> class OrangeDetector(scrubadub.detectors.Detector):
    ...     name = 'orange'
    ...     def iter_filth(self, text: str, document_name: 'Optional[str]' = None) -> 'Generator[Filth, None, None]':
    ...         # This detector always returns this same Filth no matter the input.
    ...         # You should implement something better here.
    ...         yield FruitFilth(beg=0, end=7, text='Oranges', document_name=document_name, detector_name=self.name)

    >>> scrubber = scrubadub.Scrubber()
    >>> scrubber.add_detector(OrangeDetector)
    >>> text = "Oranges grow in my garden."
    >>> scrubber.clean(text)
    '{{FRUIT}} grow in my garden.'

The ``type`` attribute of the ``FruitFilth`` gives a name to the type of filth that you are representing with this new
filth class and this is what will replace the dirty text after it has been scrubbed clean.
In the above example you can see ``"Oranges"`` is replaced by ``"{{FRUIT}}"`` and the ``FRUIT`` comes from the uppercase of ``FruitFilth.type``.

When initialising your ``Filth`` in the ``Detector.iter_filth`` function, be
sure to pass on the name of the document and the name of the detector that
found the filth.
While this isn't required, passing the name of the detector allows the Detector
comparison functions to work and passing the name of the document allows batch
analysis of related documents with one call to the `Scrubber`.


Regex-based detectors
---------------------

One of the most common ways to remove items from text is with a regex, below is a more complete example showing this.

.. code:: pycon

    >>> import scrubadub, re

    >>> class FruitFilth(scrubadub.filth.Filth):
    ...     type = 'fruit'

    >>> class OrangeDetector(scrubadub.detectors.Detector):
    ...     name = 'orange'
    ...     regex = re.compile("orange(s)?", re.IGNORECASE)
    ...     filth_cls = FruitFilth
    ...     def iter_filth(self, text: str, document_name: 'Optional[str]' = None) -> 'Generator[Filth, None, None]':
    ...         for match in self.regex.finditer(text):
    ...             yield self.filth_cls(match=match, detector_name=self.name, document_name=document_name,
    ...                                  locale=self.locale)

    >>> scrubber = scrubadub.Scrubber()
    >>> scrubber.add_detector(OrangeDetector)
    >>> text = "Oranges grow in my garden."
    >>> scrubber.clean(text)
    '{{FRUIT}} grow in my garden.'

However, there is a lot of code that is in the ``iter_filth(...)`` function that is rather boring and boiler plate.
For this reason we have provided a :ref:`scrubadub.detectors.RegexDetector` that handles this (and more!) for you,
so that you can focus on the regex.

.. code:: pycon

    >>> import scrubadub, re

    >>> class FruitFilth(scrubadub.filth.Filth):
    ...     type = 'fruit'

    >>> class OrangeDetector(scrubadub.detectors.RegexDetector):
    ...     name = 'orange'
    ...     regex = re.compile("orange(s)?", re.IGNORECASE)
    ...     filth_cls = FruitFilth

    >>> scrubber = scrubadub.Scrubber()
    >>> scrubber.add_detector(OrangeDetector)
    >>> text = "Oranges grow in my garden."
    >>> scrubber.clean(text)
    '{{FRUIT}} grow in my garden.'

To use it, ensure your ``Detector`` inherits from the ``scrubadub.detectors.RegexDetector`` and define a ``regex`` and
``filth_cls`` attribute as above.

Registration and auto-loading
-----------------------------

To ensure that the ``Scrubber`` class knows about your detector you should register it with the detector catalogue;
this can be done using the :ref:`scrubadub.detectors.register_detector` decorator.
The ``Scrubber`` looks for detectors in this catalogue when when searching for the detectors that should be included
automatically and when adding or removing a detector by name.
By registering a detector and setting ``autoload = True`` the detector will be automatically loaded when the
``Scrubber`` is initialised without a specific ``detector_list`` argument.

.. code:: pycon

    >>> import scrubadub, re

    >>> class FruitFilth(scrubadub.filth.Filth):
    ...     type = 'fruit'

    >>> @scrubadub.detectors.register_detector
    ... class OrangeDetector(scrubadub.detectors.Detector):
    ...     name = 'orange'
    ...     regex = re.compile("orange(s)?", re.IGNORECASE)
    ...     autoload = True
    ...     filth_cls = FruitFilth
    ...     def iter_filth(self, text: str, document_name: 'Optional[str]' = None) -> 'Generator[Filth, None, None]':
    ...         for match in self.regex.finditer(text):
    ...             yield self.filth_cls(match=match, detector_name=self.name, document_name=document_name,
    ...                                  locale=self.locale)

    >>> scrubber = scrubadub.Scrubber()
    >>> text = "Oranges grow in my garden."
    >>> scrubber.clean(text)
    '{{FRUIT}} grow in my garden.'
    >>> scrubber.remove_detector('orange')
    >>> scrubber.clean(text)
    'Oranges grow in my garden.'

If you create a package for your new detector, the decorator wouldn't be run until import.
To ensure that the scrubadub detector catalogue knows about your new detector (even in a separate package that has
not been imported), you can use python entry points.

Following from the above example, if we create a ``scrubadub_fruit`` package and place the ``OrangeDetector`` in the
``scrubadub_fruit.detectors`` namespace, we could add the following into our ``setup.cfg`` to register it with the
scrubadub detector catalogue:

.. code::

    [options.entry_points]
    scrubadub_detectors =
        orange = scrubadub_fruit.detectors:OrangeDetector

More information about entry points can be found in the
`setuptools documentation <https://setuptools.readthedocs.io/en/latest/userguide/entry_point.html>`_.

Batch processing
----------------

Sometimes processing documents in batches can greatly speed up the time taken to process a group of documents, for
example when passing documents to large machine learning models.
Because of this, you can also define a ``iter_filth_documents(self, document_list, document_names)`` function, which
takes precedence over the ``iter_filth(self, text, document_name=None)`` function.
Below is an alternitive implemtation of the ``OrangeDetector`` utilising ``iter_filth_documents(...)``.

.. code:: pycon

    >>> import scrubadub, re

        >>> class FruitFilth(scrubadub.filth.Filth):
        ...     type = 'fruit'

        >>> class OrangeDetector(scrubadub.detectors.Detector):
        ...     name = 'orange'
        ...     regex = re.compile("orange(s)?", re.IGNORECASE)
        ...     filth_cls = FruitFilth
        ...     def iter_filth_documents(self, document_list: 'Sequence[str]',
        ...                              document_names: 'Sequence[Optional[str]]') -> 'Generator[Filth, None, None]':
        ...         for text, document_name in zip(document_list, document_names):
        ...             for match in self.regex.finditer(text):
        ...                 yield self.filth_cls(match=match, detector_name=self.name, document_name=document_name,
        ...                                      locale=self.locale)

        >>> scrubber = scrubadub.Scrubber(detector_list=[OrangeDetector()])
        >>> scrubber.clean('Oranges grow in my garden.')
        '{{FRUIT}} grow in my garden.'

    Note that for a given detector only one of either

        >>> class FruitFilth(scrubadub.filth.Filth):
        ...     type = 'fruit'

        >>> class OrangeDetector(scrubadub.detectors.Detector):
        ...     name = 'orange'
        ...     regex = re.compile("orange(s)?", re.IGNORECASE)
        ...     filth_cls = FruitFilth
        ...     def iter_filth_documents(self, document_list: 'Sequence[str]',
        ...                              document_names: 'Sequence[Optional[str]]') -> 'Generator[Filth, None, None]':
        ...         for text, document_name in zip(document_list, document_names):
        ...             for match in self.regex.finditer(text):
        ...                 yield self.filth_cls(match=match, detector_name=self.name, document_name=document_name,
        ...                                      locale=self.locale)

        >>> scrubber = scrubadub.Scrubber(detector_list=[OrangeDetector()])
        >>> scrubber.clean('Oranges grow in my garden.')
        '{{FRUIT}} grow in my garden.'

    Note that for a given detector only one of either

    >>> class FruitFilth(scrubadub.filth.Filth):
    ...     type = 'fruit'

    >>> class OrangeDetector(scrubadub.detectors.Detector):
    ...     name = 'orange'
    ...     regex = re.compile("orange(s)?", re.IGNORECASE)
    ...     filth_cls = FruitFilth
    ...     def iter_filth_documents(self, document_list: 'Sequence[str]',
    ...                              document_names: 'Sequence[Optional[str]]') -> 'Generator[Filth, None, None]':
    ...         for text, document_name in zip(document_list, document_names):
    ...             for match in self.regex.finditer(text):
    ...                 yield self.filth_cls(match=match, detector_name=self.name, document_name=document_name,
    ...                                      locale=self.locale)

    >>> scrubber = scrubadub.Scrubber(detector_list=[OrangeDetector()])
    >>> scrubber.clean('Oranges grow in my garden.')
    '{{FRUIT}} grow in my garden.'

Note that for a given detector only one of either ``iter_filth_documents(self, document_list, document_names)`` or
``iter_filth(self, text, document_name=None)`` needs to be defined, not both.

Localization
------------

We beleive that localization of ``Detectors`` is very important for the future of ``scrubadub`` and so we have an
entire page page dedicated to this topic: :ref:`localization`.
But to give you a quick preview, you can specify a class method in your ``Detector`` called ``supported_locale``,
that lets the ``Scrubber`` know if the ``OrangeDetector`` (in the example below) supports a given language or region.

.. code:: pycon

    >>> import scrubadub
    >>> class OrangeDetector(scrubadub.detectors.RegexDetector):
    ...     ...
    ...     @classmethod
    ...     def supported_locale(cls, locale: str) -> bool:
    ...         language, region = cls.locale_split(locale)
    ...         return language in ['en']

Validation
----------

Sometimes a regex isn't sufficient to know if you've found valid filth or not and you need something more complicated
in a python function.
A classic example of this is `credit card number validation <https://en.wikipedia.org/wiki/Luhn_algorithm>`_, where
simply selecting all 16-digit numbers would lead to many other 16-digit numbers being marked incorrectly as credit
cards.

There are a couple of ways that you could deal with this you could write your own ``iter_filth`` function that finds
the credit card numbers in the text and then validates them, or you could use the ``RegexDetector`` in combination with
the ``Filth.is_valid()`` function.

The ``Filth.is_valid()`` function is called by the ``Scrubber`` for each instance of filth that is found.
If ``Filth.is_valid()`` returns ``False``, the ``Filth`` is ignored by the ``Scrubber`` and treated as clean text.

Both methods outlines above are valid ways to solve this problem, but the ``Filth.is_valid()`` method is particularly
useful if multiple ``Detector``\ s return the same ``Filth`` (perhaps two seperate methods for detecting the same
``Filth`` have been created in two ``Detectors``).
An example using ``Filth.is_valid()`` is given below:

.. code:: pycon

    >>> import scrubadub, string, stdnum.luhn, re

    >>> class VisaCardNumberFilth(scrubadub.filth.Filth):
    ...     type = 'visa_card_number'
    ...
    ...     def is_valid(self) -> bool:
    ...         return stdnum.luhn.is_valid(self.text)

    >>> class VisaCardNumberDetector(scrubadub.detectors.RegexDetector):
    ...     name = 'visa'
    ...     filth_cls = VisaCardNumberFilth
    ...     autoload = False
    ...     regex = re.compile(r"\b4[0-9]{12}(?:[0-9]{3})?\b")

    >>> scrubber = scrubadub.Scrubber(detector_list=[VisaCardNumberDetector])
    >>> scrubber.clean('My reservation ID is 4343457563243982, please charge my room to the card 4829675671235307')
    'My reservation ID is 4343457563243982, please charge my room to the card {{VISA_CARD_NUMBER}}'
