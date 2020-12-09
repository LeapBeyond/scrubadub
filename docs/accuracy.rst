.. _comparison:

Accuracy
========

The most common question that people have about scrubadub is:

    How accurately can scrubadub detect PII?

It's a great question that's hard, but essential to answer.

It is straightforward to measure this on pseudo-data (fake data that is generated), but its not clear how applicable this is to real-world applications.
There might be the possibility a possibility to use some open real-world datasets, but it's not clear if such things exist given the sensitivity of PII.

We show the precision and recall for each of the `Filth` types detected by the various `Detector`\ s.
`Wikipedia <https://en.wikipedia.org/wiki/Precision_and_recall>`_ has a good explanation, but these are defined as:

- **Precision:** Percentage of true `Filth` detected out of all `Filth` selected by the `Detector`

  - If this is low, there is lots of clean text incorrectly detected as `Filth`

- **Recall:** Percentage of the true `Filth` that is selected by the `Detector`

  - If this is low, there is lots of dirty text that is not detected as `Filth`

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

First data must be obtained with PII in and it must be tagged as true PII, usually by a human.
If you cannot get real data, you can generate fake data, but this is never as good; the function ``make_fake_document()`` below makes a fake document and provides the known filth items needed for the `KnownFilthDetector`.

Once this is done you can add the ``KnownFilthDetector`` to your scrubber and provide it with your known true Filth.
Then you can use the ``get_filth_classification_report(filth_list)`` function to get a report containing the recall and precision of the detectors.
In addition to this classification report, there is also the ``get_filth_dataframe(filth_list)`` function that returns a pandas `DataFrame` that can be used to get more information on the types of `Filth` that were detected.

.. autofunction:: scrubadub.comparison.get_filth_classification_report
    :noindex:

.. autofunction:: scrubadub.comparison.get_filth_dataframe
    :noindex:

.. autofunction:: scrubadub.comparison.make_fake_document
    :noindex:




