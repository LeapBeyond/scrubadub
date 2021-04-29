.. _advanced_usage:
.. _usage:

Usage
=====

By default, `scrubadub` removes content from text that may
reveal personal identity, but there are certainly circumstances where you may
want to customize the behavior of `scrubadub`. This section outlines a few of
these use cases. If you don't see your particular use case here, please take a
look :ref:`under the hood <api_scrubadub>` and :ref:`contribute
<contributing>` it back to the documentation!

Anatomy of scrubadub
--------------------

``scrubadub`` consists of four separate components:

* ``Filth`` objects are used to identify specific parts of the dirty
  dirty text that contains sensitive information.

* ``Detector`` objects are used to detect specific types of ``Filth``.

* ``PostProcessor`` objects are used to alter the found ``Filth``.
  This could be to replace the ``Filth`` with a hash or token.

* The ``Scrubber`` is responsible for managing the cleaning process.
  It keeps track of the ``Detector``, ``PostProcessor`` and ``Filth`` objects.
  It also resolves conflicts that may arise between different ``Detector``
  objects.

Adding an optional detector
---------------------------

To add an optional detector, first ensure the detector has been imported, then create a scrubber, add the detector and then scrub away.
This is shown below:

.. code:: pycon

    >>> import scrubadub, scrubadub.detectors.spacy
    >>> scrubber = scrubadub.Scrubber()
    >>> scrubber.add_detector(scrubadub.detectors.spacy.SpacyEntityDetector)
    >>> scrubber.clean("My name is John")
    'My name is {{NAME}}'

In the table below you can see which detectors are included by default and which ones arent.
For more infomation about these detectors checkout :ref:`the detector documentation <api_scrubadub_detectors>`

+----------------------------------------+----------------------------------------+
| Default detectors                      | Optional detectors                     |
+========================================+========================================+
| | ``CredentialDetector``               | | ``AddressDetector``                  |
| | ``CreditCardDetector``               | | ``DateOfBirthDetector``              |
| | ``DriversLicenceDetector``           | | ``SkypeDetector``                    |
| | ``EmailDetector``                    | | ``SpacyEntityDetector``              |
| | ``NationalInsuranceNumberDetector``  | | ``StanfordEntityDetector``           |
| | ``PhoneDetector``                    | | ``TaggedEvaluationFilthDetector``    |
| | ``PostalCodeDetector``               | | ``TextBlobNameDetector``             |
| | ``SocialSecurityNumberDetector``     | | ``UserSuppliedFilthDetector``        |
| | ``TaxReferenceNumberDetector``       | |                                      |
| | ``TwitterDetector``                  | |                                      |
| | ``UrlDetector``                      | |                                      |
| | ``VehicleLicencePlateDetector``      | |                                      |
+----------------------------------------+----------------------------------------+

Localisation
------------

If you don't happen to speak english or live in the US, you will find the localisation super useful.
You can tell the scrubber which locale to use.

.. code:: pycon

    >>> import scrubadub, scrubadub.detectors.spacy
    >>> scrubber = scrubadub.Scrubber(locale='de_DE')
    >>> scrubber.clean('Meine Telefonnummer ist 05086 63680')
    'Meine Telefonnummer ist {{PHONE}}'

If you're not sure about the format of the locale code, if you want more examples or if you want to build a localised detector, checkout :ref:`our documentation on localisation <localization>`.

Suppressing a detector
----------------------

In some instances, you may wish to suppress a particular detector from removing
information. For example, if you have a specific reason to keep email addresses
in the resulting output, you can disable the email address cleaning like this:

.. code:: pycon

    >>> import scrubadub
    >>> scrubber = scrubadub.Scrubber()
    >>> scrubber.remove_detector('email')
    >>> text = "contact Joe Duffy at joe@example.com"
    >>> scrubber.clean(text)
    u"contact {{NAME}} {{NAME}} at joe@example.com"


Configuring a detector
----------------------

It is sometimes important to configure detectors before using them.
One example is the ``SpacyEntityDetector`` which takes a `model` argument.
In the `model` argument you can say which model spacy should use to identify named entites.
If the `model` argument is not given, it uses a model based on your locale.
To detect named entities in french you would do the following:

.. code:: pycon

    >>> import scrubadub, scrubadub.detectors.spacy
    >>> scrubber = scrubadub.Scrubber(locale='fr_FR')
    >>> detector = scrubadub.detectors.spacy.SpacyEntityDetector(model='fr_core_news_lg')
    >>> scrubber.add_detector(detector)
    >>> text = "contacter Emmanuel Pereira au 01 81 36 78 86"
    >>> scrubber.clean(text)
    'contacter {{NAME}} au {{PHONE}}'


Customizing filth markers
-------------------------

By default, `scrubadub` uses mustache notation to signify what has been removed from the dirty dirty text.
The default setup is shown below:

.. code:: pycon

    >>> import scrubadub
    >>> text = "contact Joe Duffy at joe@example.com"
    >>> scrubber = scrubadub.Scrubber(post_processor_list=[
    ...     scrubadub.post_processors.FilthReplacer(),
    ...     scrubadub.post_processors.PrefixSuffixReplacer(),
    ... ])
    >>> scrubber.clean(text)
    'contact {{NAME}} {{NAME}} at {{EMAIL}}'

This can be inconvenient in situations where you want to display the information differently.
You can alter the arguments passed to the ``scrubadub.post_processors.FilthReplacer`` constructor to include the
filth type, a number unique to that filth and a hash of that filth, see the
:ref:`post_processors reference <api_scrubadub_post>` for the set of options available.
You can also customize the mustache notation by setting the `prefix` and `suffix` arguments in the
``scrubadub.post_processors.PrefixSuffixReplacer`` constructor.
As an example, to display a hash of the Filth in bold HTML, you could to do this:

.. code:: pycon

    >>> import scrubadub
    >>> text = "contact Joe Duffy at joe@example.com"
    >>> scrubber = scrubadub.Scrubber(post_processor_list=[
    ...     scrubadub.post_processors.FilthReplacer(include_hash=True, hash_salt='example', hash_length=5),
    ...     scrubadub.post_processors.PrefixSuffixReplacer(prefix='<b>', suffix='</b>'),
    ... ])
    >>> scrubber.clean(text)
    'contact <b>NAME-C6347</b> <b>NAME-01E6A</b> at <b>EMAIL-028CC</b>'


Adding and removing detectors
-----------------------------

The ``Detector``\ s included in the ``Scrubber`` can be set when initialising the ``Scrubber`` using the `detector_list` parameter.
Detectors can also be added or removed from the scrubber at any time by calling ``Scrubber.remove_detector`` and ``Scrubber.add_detector``.
These functions can be passed one of:

* a string -- the detector name
* a ``Detector`` object -- an instance of a ``Detector`` class
* a ``Detector`` class -- a ``Detector`` class

It is important to note that two ``Detector``\ s cant be added to the same ``Scrubber`` with the same name.
If you want to add two copies of the same ``Detector`` to a ``Scrubber``, you can set a `name` in the constructor.

Examples of this are given below:

.. code:: pycon

    >>> import scrubadub
    >>> # Create a detector with a name 'example_email'
    >>> detector = scrubadub.detectors.EmailDetector(name='example_email')

    >>> # Detectors can be added on Scrubber initialisation
    >>> scrubber = scrubadub.Scrubber(detector_list=[detector, ])

    >>> # add/remove a detector with a Detector instance
    >>> scrubber.remove_detector(detector)

    >>> # adds/removes detector with the default name 'email' using the class
    >>> scrubber.add_detector(scrubadub.detectors.EmailDetector)
    >>> scrubber.remove_detector(scrubadub.detectors.EmailDetector)

    >>> # Adds the scrubadub.detectors.EmailDetector detector
    >>> scrubber.add_detector('email')
    >>> scrubber.remove_detector('email')

    >>> # Add back the original instance
    >>> scrubber.add_detector(detector)

    >>> # KeyError is thrown if two detectors have the same name
    >>> scrubber.add_detector(detector)
        ...
    KeyError: 'can not add Detector "example_email" to this Scrubber, this name is already in use. Try removing it first.'


.. _create-detector:

Adding a new type of filth detector
-----------------------------------

It is quite common for particular use cases of `scrubadub` to require
obfuscation of specific types of filth. If you run across something that is
very general, please :ref:`contribute it back <contributing>`! In the meantime,
you can always add your own `Filth` and `Detectors` like this:

.. code:: pycon

    >>> import scrubadub

    >>> class MyFilth(scrubadub.filth.Filth):
    ...     type = 'mine'

    >>> class MyDetector(scrubadub.detectors.Detector):
    ...     name = 'my_detector'
    ...     def iter_filth(self, text, document_name=None):
    ...         # This detector always returns this same Filth no matter the input.
    ...         # You should implement something better here.
    ...         yield MyFilth(beg=0, end=8, text='My stuff', document_name=document_name, detector_name=self.name)

    >>> scrubber = scrubadub.Scrubber()
    >>> scrubber.add_detector(MyDetector)
    >>> text = "My stuff can be found there."
    >>> scrubber.clean(text)
    u"{{MINE}} can be found there."

When initialising your `Filth` in the `Detector.iter_filth` function, be
sure to pass on the name of the document and the name of the detector that
found the filth.
While this isn't required, passing the name of the detector allows the Detector
comparison functions to work and passing the name of the document allows batch
analysis of related documents with one call to the `Scrubber`.



Adding a new type of post processor
-----------------------------------

You can add a new type of `PostProcessor` using the example below.
So far the `PostProcessor`\ s in `scrubadub` are focused on setting the `Filth`\ s `replacement_string` variable (which eventually replaces the Filth in the cleaned text).
However, `PostProcessor`\ s could be used for many tasks including validation and grouping similar `Filth` together.


.. code:: pycon

    >>> import scrubadub

    >>> class PIIReplacer(scrubadub.post_processors.PostProcessor):
    ...     name = 'pii_replacer'
    ...     def process_filth(self, filth_list):
    ...         for filth in filth_list:
    ...             # replacement_string is what the Filth will be replaced by
    ...             filth.replacement_string = 'PII'
    ...        return filth_list

    >>> scrubber = scrubadub.Scrubber(post_processor_list=[
    ...     PIIReplacer(),
    ...     scrubadub.post_processors.PrefixSuffixReplacer(),
    ... ])
    >>> text = "contact Joe Duffy at joe@example.com"
    >>> scrubber.clean(text)
    "contact {{PII}} {{PII}} at {{PII}}"


Following the API of the `Detectors` you can similarly add and remove `PostProcessors` with ``Scrubber.remove_post_processor`` and ``Scrubber.add_post_processor``.


----------------------------

.. todo:: TKTK
