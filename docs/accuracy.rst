.. _comparison:
.. _accuracy:

Accuracy
========

The most common question that people have about scrubadub is:

    How accurately can scrubadub detect PII?

It's a great question that's hard, but essential to answer.

It is straightforward to measure this on pseudo-data (fake data that is generated), but its not clear how applicable this is to real-world applications.
There might be a possibility to use some open real-world datasets, but it's not clear if such things exist given the sensitivity of PII.

Precision and recall
--------------------

We show the precision and recall for each of the `Filth` types detected by the various `Detector`\ s.
`Wikipedia <https://en.wikipedia.org/wiki/Precision_and_recall>`_ has a good explanation, but these are defined as:

- **Precision:** Percentage of true `Filth` detected out of all `Filth` selected by the `Detector`

  - If this is low, there is lots of clean text incorrectly detected as `Filth`

- **Recall:** Percentage of the true `Filth` that is selected by the `Detector`

  - If this is low, there is lots of dirty text that is not detected as `Filth`

- **f1-score:** Combines the information in the precision and recall together (only in classification reports below)

  - If either precision or recall is low, this will also be low. This is a good summary metric of precision and recall.

Pseudo-data performance
-----------------------

This section uses data created by the Faker package to test the effectiveness of the various detectors.
Here the detectors all generally perform very well (often 100%) but this will likely not be representative on actual data.

+----------------+--------------------------+-----------+-------------+-------------+
| Filth type     | Detector                 | Locale    | Precision   | Recall      |
+================+==========================+===========+=============+=============+
| Address        | Address                  | en_GB     | 100%        | 96%         |
+----------------+--------------------------+-----------+-------------+-------------+
| Address        | Address                  | en_US     | 100%        | 74%         |
+----------------+--------------------------+-----------+-------------+-------------+
| Email          | Email                    | N/A       | 100%        | 100%        |
+----------------+--------------------------+-----------+-------------+-------------+
| Name           | Name                     | en_US     | 9%          | 100%        |
+----------------+--------------------------+-----------+-------------+-------------+
| Name           | Spacy `en_core_web_sm`   | en_US     | 57%         | 90%         |
+----------------+--------------------------+-----------+-------------+-------------+
| Name           | Spacy `en_core_web_md`   | en_US     | 60%         | 95%         |
+----------------+--------------------------+-----------+-------------+-------------+
| Name           | Spacy `en_core_web_lg`   | en_US     | 53%         | 97%         |
+----------------+--------------------------+-----------+-------------+-------------+
| Name           | Spacy `en_core_web_trf`  | en_US     | 88%         | 95%         |
+----------------+--------------------------+-----------+-------------+-------------+
| Name           | Stanford NER             | en_US     | 96%         | 90%         |
+----------------+--------------------------+-----------+-------------+-------------+
| Phone Number   | Phone Number             | en_GB     | 100%        | 100%        |
+----------------+--------------------------+-----------+-------------+-------------+
| Phone Number   | Phone Number             | en_US     | 100%        | 100%        |
+----------------+--------------------------+-----------+-------------+-------------+
| Postal code    | Postal code              | en_GB     | 100%        | 74%         |
+----------------+--------------------------+-----------+-------------+-------------+
| SSN            | SSN                      | en_US     | 100%        | 100%        |
+----------------+--------------------------+-----------+-------------+-------------+
| Twitter        | Twitter                  | N/A       | 100%        | 100%        |
+----------------+--------------------------+-----------+-------------+-------------+
| URL            | URL                      | N/A       | 100%        | 100%        |
+----------------+--------------------------+-----------+-------------+-------------+


Real data performance
---------------------

We are trying to find datasets that could be used to evaluate performance; if you know of any, let us know.
Stay tuned for more updates.

Measuring performance
---------------------

Read this section if you want to measure performance on your own data.

First data must be obtained with PII in and then it must be tagged as PII, usually by a human.
The tagged PII should be in a format that is compatible with the `<scrubadub.detectors.TaggedEvaluationFilthDetector>`_.
The format needed for the ``TaggedFilthDetector`` is identical to the `<scrubadub.detectors.UserSuppliedFilthDetector>`_ which is discussed on the `usage page <user_supplied_filth_detector>`_ (essentially a list of dictionaries, each containing the text to be found and the type of filth it represents), an example is given below:

    .. code::

        [
            {"match": "wwashington@reed-ryan.org", "filth_type": "email"},
            {"match": "https://www.wong.com/", "filth_type": "url"}
        ]

In our tests we have found it useful to collect tagged PII in a CSV format that mirrors the structure of the above data; an example of this is shown in `tests/example_real_data/known_pii.csv <https://github.com/LeapBeyond/scrubadub/blob/master/tests/example_real_data/known_pii.csv>`_.
Together the tagged PII and original text documents can be loaded by a script to calculate the detector efficiencies; an example of such a script is given here
`tests/benchmark_accuracy_real_data.py <https://github.com/LeapBeyond/scrubadub/blob/master/tests/benchmark_accuracy_real_data.py>`_
A bare-bones version of the script would follow the steps:

* Load the documents (list of strings) and tagged PII (list of dictionaries)
* Initialise a ``Scrubber``, including the detectors and a ``TaggedFilthDetector`` initialised with the tagged PII
* Get the list of ``Filth``\ s found by the ``Scrubber``
* Pass the list of filth to the classification report function and print the result

This is shown in the example below, except we replace loading real data with the ``make_fake_document()`` function, which generates a fake document and fake tagged PII.
If you cannot get real data, you can generate fake data, but this is never as realistic as real data.

    .. code:: pycon

        >>> import scrubadub, scrubadub.comparison, json
        >>> document, tagged_pii = scrubadub.comparison.make_fake_document(paragraphs=1, seed=1)
        >>> print(document[:50], '...')
        Suggest shake effort many last prepare small. Main ...
        >>> print(json.dumps(tagged_pii[1:], indent=4))
        [
            {
                "match": "wwashington@reed-ryan.org",
                "filth_type": "email"
            },
            {
                "match": "https://www.wong.com/",
                "filth_type": "url"
            }
        ]
        >>> scrubber = scrubadub.Scrubber()
        >>> scrubber.add_detector(scrubadub.detectors.TaggedEvaluationFilthDetector(known_filth_items=tagged_pii))
        >>> filth_list = list(scrubber.iter_filth(document))
        >>> print(scrubadub.comparison.get_filth_classification_report(filth_list))
        filth    detector    locale      precision    recall  f1-score   support
        <BLANKLINE>
        email    email       en_US            1.00      1.00      1.00         2
        url      url         en_US            1.00      1.00      1.00         1
        <BLANKLINE>
                              micro avg       1.00      1.00      1.00         3
                              macro avg       1.00      1.00      1.00         3
                           weighted avg       1.00      1.00      1.00         3
                            samples avg       1.00      1.00      1.00         3
        <BLANKLINE>

In addition to this classification report, there is also the ``get_filth_dataframe(filth_list)`` function that returns a pandas ``DataFrame`` that can be used to get more information on the types of ``Filth`` that were detected.


The classification report
-------------------------

This script above uses the ``get_filth_classification_report(filth_list)`` function to get a report containing the recall and precision of the detectors.
Those familiar with sklearn will notice that it is a slightly modified version of the `sklearn classification report <https://scikit-learn.org/stable/modules/generated/sklearn.metrics.classification_report.html>`_.

In the first column we show the ``Filth.type`` (e.g. email, name, address, ...), followed by the ``Detector.name`` and ``Detector.locale``.
After that we have the fields from the classification report, specifically: the precision, recall, f1-score and support (number of items of that type found in the document).

We have previously discussed the ``TaggedFilthDetector`` and the ``UserSuppliedFilthDetector``, which both look for text in a document and return ``Filth``.
The difference between them is the type of the ``Filth`` that they return:

    * The ``TaggedFilthDetector`` always returns ``TaggedEvaluationFilth``.
    * The ``UserSuppliedFilthDetector`` returns the type of filth specified (e.g. ``EmailFilth`` or ``PhoneFilth``).

It is the ``TaggedEvaluationFilth`` that is used as the truth when calculating the classification report, while the other types of ``Filth`` are used to show where a ``Detector`` identified filth.
If there is both a ``TaggedEvaluationFilth`` and another type of ``Filth`` at the same location then a detector identified a tagged piece of filth, which means that it is a true positive.
If there is only a ``TaggedEvaluationFilth`` at a location in a document, then is a false negative.
If there is only a ``Filth`` at a location in a document, then is is a false positive.
Using this you can build the classification report.

In the example below there are 4 locations with both a ``Filth`` and a ``TaggedEvaluationFilth``; these are true positives.
There is also one ``NameFilth`` alone, this is a false positive.
This leads to a precision of 80% (= 4/5) and a recall of 100% (= 4/4) in the classification report.

    .. code:: pycon

        >>> import scrubadub, scrubadub.comparison, scrubadub_spacy
        >>> document, known_filth_items = scrubadub.comparison.make_fake_document(paragraphs=1, seed=3, filth_types=['name'])
        >>> scrubber = scrubadub.Scrubber(detector_list=[scrubadub_spacy.detectors.SpacyNameDetector()])
        >>> scrubber.add_detector(scrubadub.detectors.TaggedEvaluationFilthDetector(known_filth_items=known_filth_items))
        >>> filth_list = list(scrubber.iter_filth(document))
        >>> for filth in filth_list: print(filth)
        <MergedFilth filths=[<NameFilth text='Jessica Sims' beg=112 end=124 detector_name='spacy_name' locale='en_US'>, <TaggedEvaluationFilth text='Jessica Sims' beg=112 end=124 comparison_type='name' detector_name='tagged' locale='en_US'>]>
        <MergedFilth filths=[<NameFilth text='Michelle Mayer' beg=295 end=309 detector_name='spacy_name' locale='en_US'>, <TaggedEvaluationFilth text='Michelle Mayer' beg=295 end=309 comparison_type='name' detector_name='tagged' locale='en_US'>]>
        <NameFilth text='nature activity' beg=363 end=378 detector_name='spacy_name' locale='en_US'>
        <MergedFilth filths=[<NameFilth text='Claudia Carroll' beg=495 end=510 detector_name='spacy_name' locale='en_US'>, <TaggedEvaluationFilth text='Claudia Carroll' beg=495 end=510 comparison_type='name' detector_name='tagged' locale='en_US'>]>
        <MergedFilth filths=[<NameFilth text='Laura Smith' beg=675 end=686 detector_name='spacy_name' locale='en_US'>, <TaggedEvaluationFilth text='Laura Smith' beg=675 end=686 comparison_type='name' detector_name='tagged' locale='en_US'>]>
        >>> print(scrubadub.comparison.get_filth_classification_report(filth_list))
        filth    detector      locale      precision    recall  f1-score   support
        <BLANKLINE>
        name     spacy_name    en_US            0.80      1.00      0.89         4
        <BLANKLINE>
                                micro avg       0.80      1.00      0.89         4
                                macro avg       0.80      1.00      0.89         4
                             weighted avg       0.80      1.00      0.89         4
        <BLANKLINE>


API reference
-------------

Below is the API reference for some of the functions mentioned on this page.

.. autofunction:: scrubadub.comparison.get_filth_classification_report
    :noindex:

.. autofunction:: scrubadub.comparison.get_filth_dataframe
    :noindex:

.. autofunction:: scrubadub.comparison.make_fake_document
    :noindex:




