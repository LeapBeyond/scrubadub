.. _api_scrubadub_detectors:

scrubadub.detectors
===================

``scrubadub`` consists of several ``Detector``'s, which are responsible for
identifying and iterating over the ``Filth`` that can be found in a piece of
text.

Base classes
------------

Every ``Detector`` that inherits from ``scrubadub.detectors.base.Detector``.

scrubadub.detectors.base.Detector
---------------------------------

.. autoclass:: scrubadub.detectors.base.Detector

scrubadub.detectors.base.RegexDetector
--------------------------------------

For convenience, there is also a ``RegexDetector``, which makes it easy to
quickly add new types of ``Filth`` that can be identified from regular
expressions:

.. autoclass:: scrubadub.detectors.base.RegexDetector

scrubadub.detectors.base.RegionLocalisedRegexDetector
-----------------------------------------------------

.. autoclass:: scrubadub.detectors.base.RegionLocalisedRegexDetector


Detectors enabled by default
----------------------------

These are the detectors that are enabled in the scrubber by default.

scrubadub.detectors.CredentialDetector
--------------------------------------

.. autoclass:: scrubadub.detectors.CredentialDetector

scrubadub.detectors.CreditCardDetector
--------------------------------------

.. autoclass:: scrubadub.detectors.CreditCardDetector

scrubadub.detectors.DriversLicenceDetector
------------------------------------------

.. autoclass:: scrubadub.detectors.DriversLicenceDetector

scrubadub.detectors.EmailDetector
---------------------------------

.. autoclass:: scrubadub.detectors.EmailDetector

scrubadub.detectors.NationalInsuranceNumberDetector
---------------------------------------------------

.. autoclass:: scrubadub.detectors.NationalInsuranceNumberDetector

scrubadub.detectors.PhoneDetector
---------------------------------

.. autoclass:: scrubadub.detectors.PhoneDetector

scrubadub.detectors.PostalCodeDetector
--------------------------------------

.. autoclass:: scrubadub.detectors.PostalCodeDetector

scrubadub.detectors.SocialSecurityNumberDetector
------------------------------------------------

.. autoclass:: scrubadub.detectors.SocialSecurityNumberDetector

scrubadub.detectors.TaxReferenceNumberDetector
----------------------------------------------

.. autoclass:: scrubadub.detectors.TaxReferenceNumberDetector

scrubadub.detectors.TwitterDetector
-----------------------------------

.. autoclass:: scrubadub.detectors.TwitterDetector

scrubadub.detectors.UrlDetector
-------------------------------

.. autoclass:: scrubadub.detectors.UrlDetector

scrubadub.detectors.VehicleLicencePlateDetector
-----------------------------------------------

.. autoclass:: scrubadub.detectors.VehicleLicencePlateDetector


Detectors that need to be enabled
---------------------------------

These detectors need to be imported first before they they can be added to a ``Scrubber``.

scrubadub.detectors.address.AddressDetector
-------------------------------------------

.. autoclass:: scrubadub.detectors.address.AddressDetector

scrubadub.detectors.date_of_birth.DateOfBirthDetector
-----------------------------------------------------

.. autoclass:: scrubadub.detectors.date_of_birth.DateOfBirthDetector

scrubadub.detectors.skype.SkypeDetector
---------------------------------------

.. autoclass:: scrubadub.detectors.skype.SkypeDetector

scrubadub.detectors.spacy.SpacyEntityDetector
---------------------------------------------

.. autoclass:: scrubadub.detectors.spacy.SpacyEntityDetector

scrubadub.detectors.spacy_name_title.SpacyNameDetector
------------------------------------------------------

.. autoclass:: scrubadub.detectors.spacy_name_title.SpacyNameDetector

scrubadub.detectors.stanford.StanfordEntityDetector
---------------------------------------------------

.. autoclass:: scrubadub.detectors.stanford.StanfordEntityDetector

scrubadub.detectors.TaggedEvaluationFilthDetector
-------------------------------------------------

.. autoclass:: scrubadub.detectors.TaggedEvaluationFilthDetector

scrubadub.detectors.text_blob.TextBlobNameDetector
--------------------------------------------------

.. autoclass:: scrubadub.detectors.text_blob.TextBlobNameDetector

scrubadub.detectors.UserSuppliedFilthDetector
---------------------------------------------

.. autoclass:: scrubadub.detectors.UserSuppliedFilthDetector
