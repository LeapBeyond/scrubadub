
Name Detection
==============

There are several detectors that can be used to detect names:

1. `Stanford NER <https://nlp.stanford.edu/software/CRF-NER.html>`_ detector
    * Best accuracy, requires java to be installed
2. `Spacy v3 <https://explosion.ai/blog/spacy-v3-nightly/>`_ detector
    * Almost as good as Stanford NER, but easier to install
3. `TextBlob <https://textblob.readthedocs.io/en/dev/>`_ detector
    * Has a very high false positive rate, use with caution

All of these detectors are optional and so are not enabled by default.
To enable them you must install any dependencies, import them and finally add them to your ``Scrubber``.
In the following sections examples are given for this.

Stanford NER detector
---------------------

To run the Stanford NER detector you will need both java and the nltk python package.
On debian linux, java can be installed with:

.. code-block:: console

    $ apt-get install openjdk-14-jre

And then the python dependencies can be installed with:

.. code-block:: console

    $ pip install scrubadub[stanford]

This is equivalent to

.. code-block:: console

    $ pip install nltk

Once this has been done, the ``StanfordNERDetector`` can be used with the following:

.. code-block:: pycon

    >>> import scrubadub, scrubadub.detectors.stanford
    >>> scrubber = scrubadub.Scrubber()
    >>> scrubber.add_detector(scrubadub.detectors.stanford.StanfordNERDetector)
    >>> scrubber.clean("My name is John")
    'My name is {{NAME}}'

Spacy
-----

This is the suggested named detector, since its easy to install and works pretty well.
However, this uses spacy v3 (v2 is the stable version) and so might break if spacy change things, since v3 is only in preview.
The v3 version of the entity detection works much better than in v2.

Spacy v3 requires python version >= 3.6 and < 3.9, as python 3.9 is not yet supported by spacy.

To install all dependencies for the Spacy detector you can do:

.. code-block:: console

    $ pip install scrubadub[spacy]

This is equivalent to:

.. code-block:: console

    $ pip install spacy-nightly[transformers]>=3.0.0rc1

Then to run it you can add it to your ``Scrubber``, like so:

.. code-block:: pycon

    >>> import scrubadub, scrubadub.detectors.spacy
    >>> scrubber = scrubadub.Scrubber()
    >>> scrubber.add_detector(scrubadub.detectors.spacy.SpacyEntityDetector)
    >>> scrubber.clean("My name is John")
    'My name is {{NAME}}'

It is also possible to enable other tags from the Spacy Entity tagger, such Location and Organisation.
This can be done with the ``enable_*`` parameters in the initialiser:

.. code-block:: pycon

    >>> import scrubadub, scrubadub.detectors.stanford
    >>> scrubber = scrubadub.Scrubber()
    >>> scrubber.add_detector(scrubadub.detectors.stanford.StanfordNERDetector(
    ...     enable_person=True, enable_organization=True, enable_location=True
    ... ))
    >>> scrubber.clean("My name is John and I work at the United Nations")
    'My name is {{NAME}} and I work at the {{ORGANIZATION}}'

TextBlob
--------

It is suggested not to use this detector due to its high false positive rate, however it is useful in some situations.
Please test it on your data to ensure it works well.

To install all dependencies for the TextBlob detector you can do:

.. code-block:: console

    $ pip install scrubadub[textblob]

This is equivalent to:

.. code-block:: console

    $ pip install textblob

Then to run it you can add it to your ``Scrubber``, like so:

.. code-block:: pycon

    >>> import scrubadub, scrubadub.detectors.text_blob
    >>> scrubber = scrubadub.Scrubber()
    >>> scrubber.add_detector(scrubadub.detectors.text_blob.TextBlobNameDetector)
    >>> scrubber.clean("My name is John")
    'My name is {{NAME}}'

