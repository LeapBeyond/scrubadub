Change Log
==========

This project uses `semantic versioning <http://semver.org/>`_ to
track version numbers, where backwards incompatible changes
(highlighted in **bold**) bump the major version of the package.


latest changes in development for next release
----------------------------------------------

.. THANKS FOR CONTRIBUTING; MENTION WHAT YOU DID IN THIS SECTION HERE!

2.0.0
-----

There have been some changes in the scrubadub API, but few breaking changes.
The changes include:

* Several new detectors have been added (spacy, stanford NER, tax reference number, credit card, ...)
* Added ability to easily evaluate a `Detector`\ 's performance, see :ref:`accuracy`.
* Started to localise detectors to function for more than one language/location.
* Support for scrubbing multiple documents together.
* Introduced the concept of a `PostProcessor`.
  This will allow more complex groupings of `Filth`\ s and new types of tokenization.

Scrubber
^^^^^^^^

* `Detector`\ s and `PostProcessor`\ s can be added and removed using a string containing their default name, their class or an instance.
* You can clean multiple documents with one `Scrubber().clean_documents(docs)` call
* **A default set of Detectors are loaded instead of all Detectors.**
  This is particularly useful for detectors that are slow or have complex dependencies, as they dont need to be loaded each time.
  However, this might need an explicit `Scrubber().add_detector(detector)` call for the same behaviour as before.
* Added a `locale` parameter to the `Scrubber` initialiser.
* A Scrubber will only auto-load detectors that support a given `Scrubber` `locale`.

Detectors
^^^^^^^^^

* The the name of the detector has been separated from the type of filth found.
  This means multiple instances of the same detector (configured differently) can be in the same `Scrubber` instance and one `Detector` can return multiple types of `Filth`.
* **Detectors now required to define an attribute called name**, which should be unique within a `Scrubber` instance.
* **Detectors are now passed a locale argument to the Detector initialiser**.
* `Detectors have an optional `supported_locale(locale)` function that returns a bool to indicate if a given `Detector` supports a `locale`.
* **Regular expressions used by the `egexDetector class have been moved from RegexFilth.regex to RegexDetector.regex**.
* **Renamed SSNDetector to SocialSecurityNumberDetector**.
* New `AddressDetector`, which detects US, CA and GB addresses.
* New `CreditCardDetector`, which detects credit card numbers (based on the Detector in the `alphagov scrubadub fork <https://github.com/alphagov/scrubadub>`_).
* New `DateOfBirthDetector`, which detects dates of birth (thanks to `@mirandachong <https://github.com/mirandachong>`_).
* New `DriversLicenceDetector`, which detects GB drivers licence numbers.
* New `TaggedEvaluationFilthDetector`, which is used to tag real filth in text when you're evaluating the quality of your filth removal.
* New `UserSuppliedFilthDetector`, which is used to find bits of Filth that you know will be in the text.
* New `PostalCodeDetector`, which detects GB post codes.
* New `SpacyEntityDetector`, which detects a `range of named entities <https://spacy.io/api/annotation#named-entities>`_, including names (thanks to `@aCampello <https://github.com/aCampello>`_).
* New `StanfordEntityDetector`, which also detects `slightly different range of named entities <https://nlp.stanford.edu/software/CRF-NER.html#Models>`_, including names.
* New `NationalInsuranceNumberDetector`, which detects GB National Insurance Numbers (NINO) (thanks to `@mirandachong <https://github.com/mirandachong>`_).
* New `TaxReferenceNumberDetector`, which detects GB Tax Reference Numbers (TRN) (thanks to `@mirandachong <https://github.com/mirandachong>`_).
* New `VehicleLicencePlateDetector`, which detects number plates on GB cars (based on the Detector in the `alphagov scrubadub fork <https://github.com/alphagov/scrubadub>`_).
* New `RegionLocalisedRegexDetector`, which derived from the convenience class `RegexDetector` to allow for quickly creating regional regex based detectors.

Filth
^^^^^

* **Introduced three parameters in the constructor `detector_name`, `document_name` and `locale`**.
  These keep track of the `Detector` that found the `Filth`, the document it came from and the documents locale.
  This results in `Filth` objects being passed additional parameters on initialisation.
  If you have defined custom `Filth`\ s they will need to be updated so that `Filth.__init__` accepts the `detector_name`, `document_name` and `locale` keywords and call the base class constructor.

PostProcessors
^^^^^^^^^^^^^^

* Introduction of simple `PostProcessors`:
   * `FilthReplacer`: Replace the filth with the type of filth ``example@example.com -> EMAIL``, a configurable hash ``example@example.com -> 196aa39e9f8159ec`` or a monotonically increasing number for each unique piece of filth (optionally including the filth type) ``example@example.com -> EMAIL-1``.
   * `PrefixSuffixReplacer`: Add a prefix and/or suffix onto the replacement ``EMAIL-1 -> {{EMAIL-1}}``
* It is envisioned that other more complex operations can be done here too such as grouping filth (e.g. "John", "John Doe" and "Mr. Doe" could be grouped together).

1.2.2
-----

`LeapBeyond <http://leapbeyond.ai/>`_ are now supporting scrubadub with maintanance and development.

* bug fixes:

  * StopIteration no longer supported in recent python varions (`#41`_ via `@roman-y-korolev`_)

  * Fix test runner with python 3 (`#42`_ via `@roman-y-korolev`_)

  * Update documentation to reflect new repository location (`#49`_)

This is the last version that will be explicitly compatible with python 2.7.

1.2.1
-----

* bug fixes:

  * bumped ``textblob`` version (`#43`_ via `@roman-y-korolev`_)

  * fixed documentation (`#32`_ via `@ivyleavedtoadflax`_)

1.2.0
-----

* added python 3 compatability (`#31`_ via `@davidread`_)

1.1.1
-----

* fixed ``FilthMergeError`` (`#29`_ via `@hugofvs`_)

1.1.0
-----

* regular expression detection of Social Security Numbers (`#17`_)

* Added functionality to keep ``replace_with = "identifier"`` (`#21`_)

* several bug fixes, including:

   * inaccurate name detection (`#19`_)

1.0.3
-----

* minor change to force ``Detector.filth_cls`` to exist (`#13`_)

1.0.1
-----

* several bug fixes, including:

  * installation bug (`#12`_)

1.0.0
-----

* **major update to process Filth in parallel** (`#11`_)

0.1.0
-----

* added skype username scrubbing (`#10`_)

* added username/password scrubbing (`#4`_)

* added phone number scrubbing (`#3`_)

* added URL scrubbing, including URL path removal (`#2`_)

* make sure unicode is passed to ``scrubadub`` (`#1`_)

* several bug fixes, including:

  * accuracy issues with things like "I can be reached at 312.456.8453" (`#8`_)

  * accuracy issues with usernames that are email addresses (`#9`_)


0.0.1
-----

* initial release, ported from past projects

.. list of contributors that are linked to above. putting links here
   to make the text above relatively clean

.. _@davidread: https://github.com/davidread
.. _@deanmalmgren: https://github.com/deanmalmgren
.. _@hugofvs: https://github.com/hugofvs
.. _@ivyleavedtoadflax: https://github.com/ivyleavedtoadflax
.. _@roman-y-korolev: https://github.com/roman-y-korolev


.. list of issues that have been resolved. putting links here to make
   the text above relatively clean

.. _#1: https://github.com/LeapBeyond/scrubadub/issues/1
.. _#2: https://github.com/LeapBeyond/scrubadub/issues/2
.. _#3: https://github.com/LeapBeyond/scrubadub/issues/3
.. _#4: https://github.com/LeapBeyond/scrubadub/issues/4
.. _#8: https://github.com/LeapBeyond/scrubadub/issues/8
.. _#9: https://github.com/LeapBeyond/scrubadub/issues/9
.. _#10: https://github.com/LeapBeyond/scrubadub/issues/10
.. _#11: https://github.com/LeapBeyond/scrubadub/issues/11
.. _#12: https://github.com/LeapBeyond/scrubadub/issues/12
.. _#13: https://github.com/LeapBeyond/scrubadub/issues/13
.. _#17: https://github.com/LeapBeyond/scrubadub/issues/17
.. _#19: https://github.com/LeapBeyond/scrubadub/issues/19
.. _#21: https://github.com/LeapBeyond/scrubadub/issues/21
.. _#29: https://github.com/LeapBeyond/scrubadub/issues/29
.. _#31: https://github.com/LeapBeyond/scrubadub/pull/31
.. _#32: https://github.com/LeapBeyond/scrubadub/pull/32
.. _#41: https://github.com/LeapBeyond/scrubadub/pull/41
.. _#42: https://github.com/LeapBeyond/scrubadub/pull/42
.. _#43: https://github.com/LeapBeyond/scrubadub/pull/43
.. _#49: https://github.com/LeapBeyond/scrubadub/pull/49
