.. _api_scrubadub_detectors:

scrubadub.detectors
===================

``scrubadub`` consists of several ``Detector``'s, which are responsible for
identifying and iterating over the ``Filth`` that can be found in a piece of
text.

Base classes
------------

Every ``Detector`` that inherits from ``scrubadub.detectors.base.Detector``.

scrubadub.detectors.Detector
----------------------------

.. autoclass:: scrubadub.detectors.Detector

scrubadub.detectors.RegexDetector
---------------------------------

For convenience, there is also a ``RegexDetector``, which makes it easy to
quickly add new types of ``Filth`` that can be identified from regular
expressions:

.. autoclass:: scrubadub.detectors.RegexDetector

scrubadub.detectors.RegionLocalisedRegexDetector
------------------------------------------------

.. autoclass:: scrubadub.detectors.RegionLocalisedRegexDetector


Detectors enabled by default
----------------------------

These are the detectors that are enabled in the scrubber by default.

scrubadub.detectors.CredentialDetector
--------------------------------------

.. autoclass:: scrubadub.detectors.CredentialDetector

scrubadub.detectors.EmailDetector
---------------------------------

.. autoclass:: scrubadub.detectors.EmailDetector

scrubadub.detectors.PhoneDetector
---------------------------------

.. autoclass:: scrubadub.detectors.PhoneDetector

scrubadub.detectors.SSNDetector
-------------------------------

.. autoclass:: scrubadub.detectors.SSNDetector

scrubadub.detectors.UrlDetector
-------------------------------

.. autoclass:: scrubadub.detectors.UrlDetector


Detectors that need to be enabled
---------------------------------

These detectors need to be imported first before they they can be added to a ``Scrubber``.

scrubadub.detectors.DateOfBirthDetector
---------------------------------------

.. autoclass:: scrubadub.detectors.DateOfBirthDetector

scrubadub.detectors.KnownFilthDetector
--------------------------------------

.. autoclass:: scrubadub.detectors.KnownFilthDetector

scrubadub.detectors.SpacyEntityDetector
---------------------------------------

.. autoclass:: scrubadub.detectors.SpacyEntityDetector

scrubadub.detectors.SkypeDetector
---------------------------------

.. autoclass:: scrubadub.detectors.SkypeDetector

scrubadub.detectors.StanfordNERDetector
---------------------------------------

.. autoclass:: scrubadub.detectors.StanfordNERDetector

scrubadub.detectors.TextBlobNameDetector
----------------------------------------

.. autoclass:: scrubadub.detectors.TextBlobNameDetector
