import re
import copy
import random
import phonenumbers

from faker import Faker

from . import filth
from .filth import Filth
from .detectors.known import KnownFilthItem

from typing import List, Dict, Union, Optional, Tuple
import pandas as pd
import sklearn.metrics


def get_filth_classification_report(
        filth_list: List[filth.Filth],
        output_dict: bool = False,
) -> Optional[Union[str, Dict[str, float]]]:
    """Evaluates the performance of detectors using KnownFilth.

    An example of using this is shown below:

    .. code:: pycon

        >>> import scrubadub, scrubadub.comparison
        >>> scrubber = scrubadub.Scrubber(detector_list=[
        ...     scrubadub.detectors.NameDetector(name='name_detector'),
        ...     scrubadub.detectors.KnownFilthDetector([
        ...         {'match': 'Tom', 'comparison_type': 'name'},
        ...         {'match': 'tom@example.com', 'comparison_type': 'email'},
        ...     ]),
        ... ])
        >>> filth_list = list(scrubber.iter_filth("Hello I am Tom"))
        >>> print(scrubadub.comparison.get_filth_classification_report(filth_list))
                                precision    recall  f1-score   support

        name     name_detector       1.00      1.00      1.00         1

                      accuracy                           1.00         1
                     macro avg       1.00      1.00      1.00         1
                  weighted avg       1.00      1.00      1.00         1

    :param filth_list: The list of detected filth
    :type filth_list: A list of `Filth` objects
    :param output_dict: Return the report in JSON format, defautls to False
    :type output_dict: bool, optional
    :return: The report in JSON (a `dict`) or in plain text
    :rtype: `str` or `dict`

    """

    results = []  # type: List[Dict[str, int]]

    for filth_item in filth_list:
        sub_filths = [filth_item]
        if isinstance(filth_item, filth.base.MergedFilth):
            sub_filths = filth_item.filths

        results_row = {}
        for sub_filth in sub_filths:
            if isinstance(sub_filth, filth.KnownFilth) and sub_filth.comparison_type is not None:
                results_row['{}:{}'.format(sub_filth.comparison_type, filth.KnownFilth.type)] = 1
            else:
                results_row['{}:{}'.format(sub_filth.type, sub_filth.detector_name)] = 1

        # Dont include filth that was not produced by one of the detectors of interest
        if sum(results_row.values()) > 0:
            results.append(results_row)

    if len(results) == 0:
        return None

    results_df = pd.DataFrame(results).fillna(0).astype(int)
    results_df.columns = pd.MultiIndex.from_tuples(
        results_df.columns.str.split(':').values.tolist(),
        names=['filth_type', 'detector_name'],
    )

    known_types = [x[0] for x in results_df.columns if x[1] == filth.KnownFilth.type]
    detected_columns = [
        x for x in results_df.columns
        if x[1] != filth.KnownFilth.type and x[0] in known_types
    ]
    detected_classes = results_df.loc[:, detected_columns].values
    true_classes = results_df.loc[:, [(x[0], filth.KnownFilth.type) for x in detected_columns]].values

    if not output_dict:
        detector_name_max_length = max([len(x[1]) for x in detected_columns]) + 4
        class_labels = ["{} {}".format(x[0], x[1].rjust(detector_name_max_length)) for x in detected_columns]
    else:
        class_labels = ["{}:{}".format(*x) for x in detected_columns]

    report_labels = []
    # If there is only one label reshape the data so that
    # the classification_report interprets it less ambiguously
    if detected_classes.shape[1] == 1:
        detected_classes = detected_classes.T[0]
        true_classes = true_classes.T[0]
        report_labels = [1]
    else:
        report_labels = [class_labels.index(x) for x in sorted(class_labels)]
        class_labels = sorted(class_labels)

    report = sklearn.metrics.classification_report(
        true_classes,
        detected_classes,
        output_dict=output_dict,
        zero_division=0,
        target_names=class_labels,
        labels=report_labels,
        # **extra_args
    )
    return report


def get_filth_dataframe(filth_list: List[Filth]) -> pd.DataFrame:
    """Produces a pandas `DataFrame` to allow debugging and improving detectors.

    An example of using this is shown below:

    .. code:: pycon

        >>> import scrubadub, scrubadub.comparison
        >>> scrubber = scrubadub.Scrubber(detector_list=[
        ...     scrubadub.detectors.NameDetector(name='name_detector'),
        ...     scrubadub.detectors.KnownFilthDetector([
        ...         {'match': 'Tom', 'comparison_type': 'name'},
        ...         {'match': 'tom@example.com', 'comparison_type': 'email'},
        ...     ]),
        ... ])
        >>> filth_list = list(scrubber.iter_filth("Hello I am Tom"))
        >>> print(scrubadub.comparison.get_filth_dataframe(filth_list))
           group_id  filth_id filth_type  detector_name document_name text  beg  end \
        0         0         1       name  name_detector          None  Tom   11   14 \
           known_filth known_text  known_beg  known_end  known_comparison_type  exact_match \
        0         True        Tom         11         14                   name         True \
           partial_match  true_positive  false_positive  false_negative
        0           True           True           False           False

    :param filth_list: The list of detected filth
    :type filth_list: A list of `Filth` objects
    :return: A `pd.DataFrame` containing infomatoin about the detected `Filth`
    :rtype: `pd.DataFrame`

    """
    results = []
    for group_id, filth_item in enumerate(filth_list):
        sub_filths = [filth_item]
        if isinstance(filth_item, filth.base.MergedFilth):
            sub_filths = filth_item.filths
        for filth_id, sub_filth in enumerate(sub_filths):
            results.append({
                'group_id': group_id,
                'filth_id': filth_id,
                'filth_type': sub_filth.type,
                'detector_name': getattr(sub_filth, 'detector_name', float('nan')),
                'document_name': getattr(sub_filth, 'document_name', float('nan')),
                'text': sub_filth.text,
                'beg': sub_filth.beg,
                'end': sub_filth.end,
                'known_filth': isinstance(sub_filth, filth.KnownFilth),
                'comparison_type': getattr(sub_filth, 'comparison_type', float('nan')),
            })

    results_df = pd.DataFrame(results)
    suffix_label = '_y_suffix'

    return (
        pd.merge(
            results_df[~results_df['known_filth']],
            results_df[results_df['known_filth']][['group_id', 'text', 'beg', 'end', 'comparison_type']],
            how='outer',
            left_on=('group_id', 'filth_type'),
            right_on=('group_id', 'comparison_type'),
            suffixes=('', suffix_label)
        )
        .rename(columns=lambda x: x if not x.endswith(suffix_label) else 'known_' + x[:-len(suffix_label)])
        .assign(
            known_filth=lambda df: ~pd.isnull(df['known_text']),
            exact_match=lambda df: (df['text'] == df['known_text']).fillna(False),
            partial_match=lambda df: ((df['beg'] < df['known_end']) & (df['end'] > df['known_beg']).fillna(False)),
            true_positive=lambda df: (~pd.isnull(df['known_text'])) & (~pd.isnull(df['text'])),
            false_positive=lambda df: (pd.isnull(df['known_text'])) & (~pd.isnull(df['text'])),
            false_negative=lambda df: (~pd.isnull(df['known_text'])) & (pd.isnull(df['text'])),
        )
    )


def make_fake_document(
        paragraphs: int = 20, seed: int = 1234, faker: Optional[Faker] = None, filth_types: Optional[List[str]] = None
) -> Tuple[str, List[KnownFilthItem]]:
    """Creates a fake document containing `Filth` that needs to be removed. Also returns the list of known filth
    items that are needed byt the `KnownFilthDetector`\\ .

    An example of using this is shown below:

    .. code:: pycon

        >>> import scrubadub, scrubadub.comparison
        >>> document, known_filth_items = scrubadub.comparison.make_fake_document(paragraphs=1, seed=1)
        >>> scrubber = scrubadub.Scrubber()
        >>> scrubber.add_detector(scrubadub.detectors.KnownFilthDetector(known_filth_items=known_filth_items))
        >>> filth_list = list(scrubber.iter_filth(document))
        >>> print(scrubadub.comparison.get_filth_classification_report(filth_list))
                             precision    recall  f1-score   support

        twitter     twitter       1.00      1.00      1.00         1

                  micro avg       1.00      1.00      1.00         1
                  macro avg       1.00      1.00      1.00         1
               weighted avg       1.00      1.00      1.00         1

    :param paragraphs: The list of detected filth
    :type paragraphs: int
    :param seed: The random seed used to generate the document
    :type seed: int
    :param faker: A Faker object that is used to generate the text
    :type faker: int
    :param filth_types: A list of the ``Filth.type`` to generate
    :type filth_types: List[str]
    :return: The document and a list of `KnownFilthItem`\\ s
    :rtype: Tuple[str, List[KnownFilthItem]]

    """
    if faker is None:
        faker = Faker()

    def fake_phone_number():
        phone_number = ''
        results = []  # type: List[phonenumbers.PhoneNumberMatch]
        # Here I'm filtering for numbers that pass validation by the phonenumbers package
        while len(results) < 1:
            # Faker generates random numbers of the right format eg (###)###-####
            phone_number = re.sub(r'x.*$', '', Faker(locale='en_US').phone_number())
            # phonenumbers checks that they follow the rules around area codes and that they are possibly valid
            results = list(phonenumbers.PhoneNumberMatcher(phone_number, 'US'))
        return phone_number

    fake_functions = [
        (filth.address.GBAddressFilth.type, Faker(locale='en_GB').address),
        (filth.address.USAddressFilth.type, Faker(locale='en_US').address),
        (filth.EmailFilth.type, faker.email),
        (filth.NameFilth.type, faker.name),
        (filth.PhoneFilth.type, fake_phone_number),
        (filth.PostalCodeFilth.type, Faker(locale='en_GB').postcode),
        (filth.SSNFilth.type, faker.ssn),
        (filth.TwitterFilth.type, lambda: '@' + re.sub(r'[^a-zA-Z0-9_]', '', faker.user_name()[:15])),
        (filth.UrlFilth.type, faker.url),
    ]

    if filth_types is not None:
        fake_functions = [x for x in fake_functions if x[0] in filth_types]

    Faker.seed(seed)
    random.seed(seed)

    doc = ""
    known_items = []  # type: List[KnownFilthItem]
    for i_paragraph in range(paragraphs):
        for i_sentance_group in range(random.randint(1, 10)):
            text = faker.text()
            matches = list(re.finditer(r'[\s.]', text))
            position = random.choice(matches)
            pii_type, pii_function = random.choice(fake_functions)
            pii_text = pii_function()
            known_items.append({
                'match': copy.copy(pii_text),
                'filth_type': copy.copy(pii_type),
            })
            doc += (
                text[:position.start()] +
                position.group() +
                pii_text +
                position.group() +
                text[position.end():]
            )
        doc += "\n\n"
    return (doc.strip(), known_items)
