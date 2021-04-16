.. _locales:
.. _localization:

Localization
============

We have started to make scrubadub localised to support multiple languages and regions.
We are on the beginning of this journey, so stay tuned.

By setting a locale the ``Detector``\ s that need configuring based on your region or language will know what to expect.
This means that a ``Detector`` that needs to know how  ``Filth`` (such as a phone number) is formatted in your
region will be able to look for ``Filth`` in that specific format.
Other detectors that use machine learning models to identify entities in the text will be able to use models
corresponding to the correct language or location.

To set your locale you can use the standard format ``xx_YY``, where ``xx`` is a
lower-case `language code <https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes>`_
and ``YY`` is an upper-case `country code <https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2>`_.
Examples of this include ``en_CA`` (Canadian english), ``fr_CA` (Canadian french)` and ``de_AT`` (Austrian german).
These locales can be set by passing them directly to one of the functions in the ``scrubadub`` module or to a ``Scrubber`` instance:

.. code:: pycon

    >>> import scrubadub
    >>> scrubadub.clean('My US number is 731-938-1630', locale='en_US')
    'My US number is {{PHONE}}'
    >>> scrubadub.clean('My US number is 731-938-1630', locale='en_GB')
    'My US number is 731-938-1630'
    >>> scrubadub.clean('My GB number is 0121 496 0112', locale='en_GB')
    'My GB number is {{PHONE}}'
    >>> scrubadub.clean('My GB number is 0121 496 0112', locale='en_US')
    'My GB number is 0121 496 0112'
    >>> scrubber = scrubadub.Scrubber(locale='de_DE')
    >>> scrubber.clean('Meine Telefonnummer ist 05086 63680')
    'Meine Telefonnummer ist {{PHONE}}'

Below is a summary of the supported countries and regions of the various detectors in scrubadub.

 * `AddressDetector`: supports Canadian, American and British addresses
 * `PhoneDetector`: supports most regions via `libphonenumber <https://github.com/google/libphonenumber>`_
 * `PostalCodeDetector`: only supports British postcodes
 * `SpacyEntityDetector`: supports a wide range of languages check the `spacy documentation <https://spacy.io/usage/models>`_ for the full list of supported languages.
 * `StanfordEntityDetector`: only supports english in scrubadub, but the models support more languages (es, fr, de, zh).

This is just the start of the localisation, so if you want to add more languages or features we're keen to hear from you!
Other detectors are location/language independent (eg email addresses or twitter usernames) or do not support localisation.

Creating a localized detector
-----------------------------

To create a detector that is localised the process is identical to creating a normal detector
(as shown in :ref:`create-detector`), but with one addition a ``supported_locale()`` function.
If this function is not defined it is assumed that this ``Detector`` does not need
localization.
An example of a ``Detector`` that does not need localization is the email detector,
as emails follow the same format no matter where you live and what language you speak.
On the other hand, the format of a phone number can vary significantly depending on the region.

Below is an example of a detector that detects employee names for a very small, but international company.
There is one German employee, `Walther`, and one US employee `Georgina`.
When the document is German we will remove `Walther` and when the document is American we will remove `Georgina`.

The ``supported_locale()`` function should return ``True`` if the passed locale is supported and ``False`` if it is not supported.
If ``supported_locale()`` returns ``False`` then the ``Scrubber`` will emit a warning and not add or run that ``Detector`` on the documents passed to it.
The ``Detector.locale_split(locale)`` function can be used to split the locale into the language and region.

Below is the full example:

.. code:: pycon

    >>> import scrubadub

    >>> class EmployeeNameFilth(scrubadub.filth.Filth):
    ...     type = 'employee_name'

    >>> class EmployeeDetector(scrubadub.detectors.Detector):
    ...     name = 'employee_detector'
    ...
    ...     def __init__(self, **kwargs):
    ...         super(EmployeeDetector, self).(**kwargs)
    ...         self.employees = {'DE': ['Walther'], 'US': ['Georgina'] }
    ...         self.regex = re.compile('|'.join(self.employees[self.region]))
    ...
    ...     @classmethod
    ...     def supported_locale(cls, locale):
    ...         language, region = cls.locale_split(locale)
    ...         return region in ['DE', 'US']
    ...
    ...     def iter_filth(self, text, document_name=None):
    ...         for match in self.regex.finditer(text):
    ...             yield EmployeeNameFilth(match=match, detector_name=self.name, document_name=document_name, locale=self.locale)
    ...
    >>> us_scrubber = scrubadub.Scrubber(detector_list=[EmployeeDetector], locale='en_US')
    >>> us_scrubber.clean('Jane spoke with Georgina')
    'Jane spoke with {{EMPLOYEE_NAME}}'
    >>> de_scrubber = scrubadub.Scrubber(detector_list=[EmployeeDetector], locale='de_DE')
    >>> de_scrubber.clean('Jane spoke with Georgina')
    'Jane spoke with Georgina'
    >>> de_scrubber.clean('Luigi spoke with Walther')
    'Luigi spoke with {{EMPLOYEE_NAME}}'




