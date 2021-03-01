.. _comparison:
.. _accuracy:

Accuracy
========

The most common question that people have about scrubadub is:

    How accurately can scrubadub detect PII?

It's a great question that's hard, but essential to answer.

It is straightforward to measure this on pseudo-data (fake data that is generated), but its not clear how applicable this is to real-world applications.
There might be the possibility a possibility to use some open real-world datasets, but it's not clear if such things exist given the sensitivity of PII.

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

First data must be obtained with PII in and then it must be tagged as known PII, usually by a human.
The known PII should be tagged in a format that is compatible with the ``TaggedFilthDetector``; an example of this is shown in `tests/example_real_data/known_pii.csv <https://github.com/LeapBeyond/scrubadub/blob/master/tests/example_real_data/known_pii.csv>`_.
Together the known PII and original text documents can be loaded by a script to calculate the detector efficiencies; an example of such a script is given here
`tests/benchmark_accuracy_real_data.py <https://github.com/LeapBeyond/scrubadub/blob/master/tests/benchmark_accuracy_real_data.py>`_
A bare-bones version of the script is given below, where the documents and known filth is loaded, a ``Scrubber`` is initialised, the detectors are run and the classification report is printed.
In the below example we replace loading real data with the ``make_fake_document()`` function, which generates a fake document for example purposes.
If you cannot get real data, you can generate fake data, but this is never as realistic as real data.
This would need to be replaced with something to load real data such as in `the example <https://github.com/LeapBeyond/scrubadub/blob/master/tests/benchmark_accuracy_real_data.py>`_.

    .. code:: pycon

        >>> import scrubadub, scrubadub.comparison, json
        >>> document, known_filth_items = scrubadub.comparison.make_fake_document(paragraphs=1, seed=1)
        >>> print(document[:50], '...')
        Suggest shake effort many last prepare small. Main ...
        >>> print(json.dumps(known_filth_items[1:], indent=4))
        [
            {
                "match": "todd56@ryan-hanson.biz",
                "filth_type": "email"
            },
            {
                "match": "http://sheppard.com/",
                "filth_type": "url"
            }
        ]
        >>> scrubber = scrubadub.Scrubber()
        >>> scrubber.add_detector(scrubadub.detectors.TaggedEvaluationFilthDetector(known_filth_items=known_filth_items))
        >>> filth_list = list(scrubber.iter_filth(document))
        >>> print(scrubadub.comparison.get_filth_classification_report(filth_list))
        filth     detector     locale    precision    recall  f1-score   support
        <BLANKLINE>
          url          url      en_US         1.00      1.00      1.00         1
        email        email      en_US         1.00      1.00      1.00         2
        <BLANKLINE>
                              micro avg       1.00      1.00      1.00         3
                              macro avg       1.00      1.00      1.00         3
                           weighted avg       1.00      1.00      1.00         3
                            samples avg       1.00      1.00      1.00         3
        <BLANKLINE>

In addition to this classification report, there is also the ``get_filth_dataframe(filth_list)`` function that returns a pandas `DataFrame` that can be used to get more information on the types of `Filth` that were detected.


The classification report
-------------------------

This script above uses the ``get_filth_classification_report(filth_list)`` function to get a report containing the recall and precision of the detectors.
Those familiar with sklearn will notice that it is a slightly modified version of the (sklearn classification report)[https://scikit-learn.org/stable/modules/generated/sklearn.metrics.classification_report.html].

In the first column we show the ``Filth.type`` (e.g. email, name, address, ...), followed by the ``Detector.name`` and ``Detector.locale``.
After that we have the fields from the classification report, specifically: the precision, recall, f1-score and support (number of items of that type found in the document).

API reference
-------------

Below is the API reference for some of the functions mentioned on this page.

.. autofunction:: scrubadub.comparison.get_filth_classification_report
    :noindex:

.. autofunction:: scrubadub.comparison.get_filth_dataframe
    :noindex:

.. autofunction:: scrubadub.comparison.make_fake_document
    :noindex:




