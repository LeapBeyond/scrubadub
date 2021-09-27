.. _api_scrubadub_detectors:

scrubadub.detectors
===================

``scrubadub`` consists of several ``Detector``'s, which are responsible for
identifying and iterating over the ``Filth`` that can be found in a piece of
text.

Base classes
------------

Every ``Detector`` that inherits from ``scrubadub.detectors.Detector``.

.. _scrubadub.detectors.Detector:

scrubadub.detectors.Detector
----------------------------

.. autoclass:: scrubadub.detectors.Detector

.. _scrubadub.detectors.RegexDetector:

scrubadub.detectors.RegexDetector
---------------------------------

For convenience, there is also a ``RegexDetector``, which makes it easy to
quickly add new types of ``Filth`` that can be identified from regular
expressions:

.. autoclass:: scrubadub.detectors.RegexDetector

.. _scrubadub.detectors.RegionLocalisedRegexDetector:

scrubadub.detectors.RegionLocalisedRegexDetector
------------------------------------------------

.. autoclass:: scrubadub.detectors.RegionLocalisedRegexDetector


Detectors enabled by default
----------------------------

These are the detectors that are enabled in the scrubber by default.


.. _scrubadub.detectors.CredentialDetector:

scrubadub.detectors.CredentialDetector
--------------------------------------

.. autoclass:: scrubadub.detectors.CredentialDetector

.. _scrubadub.detectors.CreditCardDetector:

scrubadub.detectors.CreditCardDetector
--------------------------------------

.. autoclass:: scrubadub.detectors.CreditCardDetector

.. _scrubadub.detectors.DriversLicenceDetector:

scrubadub.detectors.DriversLicenceDetector
------------------------------------------

.. autoclass:: scrubadub.detectors.DriversLicenceDetector

.. _scrubadub.detectors.EmailDetector:

scrubadub.detectors.EmailDetector
---------------------------------

.. autoclass:: scrubadub.detectors.EmailDetector

.. _scrubadub.detectors.en_GB.NationalInsuranceNumberDetector:

scrubadub.detectors.en_GB.NationalInsuranceNumberDetector
---------------------------------------------------------

.. autoclass:: scrubadub.detectors.en_GB.NationalInsuranceNumberDetector

.. _scrubadub.detectors.PhoneDetector:

scrubadub.detectors.PhoneDetector
---------------------------------

.. autoclass:: scrubadub.detectors.PhoneDetector

.. _scrubadub.detectors.PostalCodeDetector:

scrubadub.detectors.PostalCodeDetector
--------------------------------------

.. autoclass:: scrubadub.detectors.PostalCodeDetector

.. _scrubadub.detectors.en_US.SocialSecurityNumberDetector:

scrubadub.detectors.en_US.SocialSecurityNumberDetector
------------------------------------------------------

.. autoclass:: scrubadub.detectors.en_US.SocialSecurityNumberDetector

.. _scrubadub.detectors.en_GB.TaxReferenceNumberDetector:

scrubadub.detectors.en_GB.TaxReferenceNumberDetector
----------------------------------------------------

.. autoclass:: scrubadub.detectors.en_GB.TaxReferenceNumberDetector

.. _scrubadub.detectors.TwitterDetector:

scrubadub.detectors.TwitterDetector
-----------------------------------

.. autoclass:: scrubadub.detectors.TwitterDetector

.. _scrubadub.detectors.UrlDetector:

scrubadub.detectors.UrlDetector
-------------------------------

.. autoclass:: scrubadub.detectors.UrlDetector

.. _scrubadub.detectors.VehicleLicencePlateDetector:

scrubadub.detectors.VehicleLicencePlateDetector
-----------------------------------------------

.. autoclass:: scrubadub.detectors.VehicleLicencePlateDetector


Optional detectors
------------------

These detectors need to be manually added to a ``Scrubber``, they are not loaded automatically.
An example is shown below that demonstrates the various ways that a detector can be added to a ``Scrubber``:

.. code-block:: pycon

    >>> import scrubadub
    >>> scrubber = scrubadub.Scrubber(detector_list=[scrubadub.detectors.TextBlobNameDetector()])
    >>> scrubber.add_detector(scrubadub.detectors.CreditCardDetector)
    >>> scrubber.add_detector('skype')
    >>> detector = scrubadub.detectors.DateOfBirthDetector(require_context=True)
    >>> scrubber.add_detector(detector)

For further information see the :ref:`usage<usage>` page.

.. _scrubadub.detectors.DateOfBirthDetector:

scrubadub.detectors.DateOfBirthDetector
---------------------------------------

.. autoclass:: scrubadub.detectors.DateOfBirthDetector

.. _scrubadub.detectors.SkypeDetector:

scrubadub.detectors.SkypeDetector
---------------------------------

.. autoclass:: scrubadub.detectors.SkypeDetector

.. _scrubadub.detectors.TaggedEvaluationFilthDetector:

scrubadub.detectors.TaggedEvaluationFilthDetector
-------------------------------------------------

.. autoclass:: scrubadub.detectors.TaggedEvaluationFilthDetector

.. _scrubadub.detectors.TextBlobNameDetector:

scrubadub.detectors.TextBlobNameDetector
----------------------------------------

.. autoclass:: scrubadub.detectors.TextBlobNameDetector

.. _scrubadub.detectors.UserSuppliedFilthDetector:

scrubadub.detectors.UserSuppliedFilthDetector
---------------------------------------------

.. autoclass:: scrubadub.detectors.UserSuppliedFilthDetector


External detectors
------------------

These are detectors that are not included in the ``scrubadub`` package, usually because they come with large
external dependencies that are not always needed.
To use them you should first import their package and then add them to the ``Scrubber``, an example of this is shown
below:

.. code-block:: pycon

    >>> import scrubadub, scrubadub_address
    >>> scrubber = scrubadub.Scrubber()
    >>> scrubber.add_detector(scrubadub_address.detectors.AddressDetector)


.. _scrubadub_address.detectors.AddressDetector:

scrubadub_address.detectors.AddressDetector
-------------------------------------------

.. autoclass:: scrubadub_address.detectors.AddressDetector

.. _scrubadub_spacy.detectors.SpacyEntityDetector:

scrubadub_spacy.detectors.SpacyEntityDetector
---------------------------------------------

.. autoclass:: scrubadub_spacy.detectors.SpacyEntityDetector

.. _scrubadub_spacy.detectors.SpacyNameDetector:

scrubadub_spacy.detectors.SpacyNameDetector
-------------------------------------------

.. autoclass:: scrubadub_spacy.detectors.SpacyNameDetector

.. _scrubadub_stanford.detectors.StanfordEntityDetector:

scrubadub_stanford.detectors.StanfordEntityDetector
---------------------------------------------------

.. autoclass:: scrubadub_stanford.detectors.StanfordEntityDetector


Catalogue functions
-------------------

.. _scrubadub.detectors.register_detector:

scrubadub.detectors.register_detector
-------------------------------------

.. autofunction:: scrubadub.detectors.register_detector

.. _scrubadub.detectors.remove_detector:

scrubadub.detectors.remove_detector
-----------------------------------

.. autofunction:: scrubadub.detectors.remove_detector


