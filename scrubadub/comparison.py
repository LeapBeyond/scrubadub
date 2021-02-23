import re
import copy
import random

from faker import Faker

from . import filth as filth_module
from .filth import Filth
from .detectors.known import KnownFilthItem

from typing import List, Dict, Union, Optional, Tuple, Callable
import pandas as pd
import sklearn.metrics


def get_filth_classification_report(
        filth_list: List[Filth],
        combine_detectors: bool = False,
        output_dict: bool = False,
) -> Optional[Union[str, Dict[str, float]]]:
    """Evaluates the performance of detectors using KnownFilth.

    An example of using this is shown below:

    .. code:: pycon

        >>> import scrubadub, scrubadub.comparison, scrubadub.detectors.text_blob
        >>> scrubber = scrubadub.Scrubber(detector_list=[
        ...     scrubadub.detectors.TextBlobNameDetector(name='name_detector'),
        ...     scrubadub.detectors.KnownFilthDetector([
        ...         {'match': 'Tom', 'filth_type': 'name'},
        ...         {'match': 'tom@example.com', 'filth_type': 'email'},
        ...     ]),
        ... ])
        >>> filth_list = list(scrubber.iter_filth("Hello I am Tom"))
        >>> print(scrubadub.comparison.get_filth_classification_report(filth_list))
        filth          detector     locale    precision    recall  f1-score   support
        <BLANKLINE>
         name     name_detector      en_US         1.00      1.00      1.00         1
        <BLANKLINE>
                                    accuracy                           1.00         1
                                   macro avg       1.00      1.00      1.00         1
                                weighted avg       1.00      1.00      1.00         1
        <BLANKLINE>

    :param filth_list: The list of detected filth
    :type filth_list: A list of `Filth` objects
    :param combine_detectors: Combine performance of all detectors for the same filth/locale
    :type combine_detectors: bool, optional
    :param output_dict: Return the report in JSON format, defautls to False
    :type output_dict: bool, optional
    :return: The report in JSON (a `dict`) or in plain text
    :rtype: `str` or `dict`
    """
    results = []  # type: List[Dict[str, int]]
    filth_max_length = 0
    detector_name_max_length = 0
    locale_max_length = 0

    for filth_item in filth_list:
        sub_filths = [filth_item]
        if isinstance(filth_item, filth_module.base.MergedFilth):
            sub_filths = filth_item.filths

        results_row = {}
        for sub_filth in sub_filths:
            if isinstance(sub_filth, filth_module.KnownFilth) and sub_filth.comparison_type is not None:
                col_name = '{}:{}:{}'.format(sub_filth.comparison_type, filth_module.KnownFilth.type, sub_filth.locale)
                results_row[col_name] = 1
            else:
                try:
                    detector_name = sub_filth.detector_name if not combine_detectors else 'combined'
                    results_row['{}:{}:{}'.format(sub_filth.type, detector_name, sub_filth.locale)] = 1
                except AttributeError:
                    print(type(sub_filth), sub_filth)
                    raise

        # Dont include filth that was not produced by one of the detectors of interest
        if sum(results_row.values()) > 0:
            results.append(results_row)

    if len(results) == 0:
        return None

    results_df = pd.DataFrame(results).fillna(0).astype(int)
    results_df.columns = pd.MultiIndex.from_tuples(
        results_df.columns.str.split(':').values.tolist(),
        names=['filth_type', 'detector_name', 'locale'],
    )

    # Find filth types that have some known filth
    known_types = [x[0] for x in results_df.columns if x[1] == filth_module.KnownFilth.type]
    # Select columns for filth that have related known filth, but that are not known filth
    detected_columns = [
        x for x in results_df.columns
        if x[1] != filth_module.KnownFilth.type and x[0] in known_types
    ]
    detected_classes = results_df.loc[:, detected_columns].values
    # Take the detected_columns above and find their associated known counterparts
    known_cols = [(x[0], filth_module.KnownFilth.type, x[2]) for x in detected_columns]
    try:
        true_classes = results_df.loc[:, known_cols].values
    except KeyError:
        raise KeyError(f"Unable to find known filths with types: {known_cols}\n"
                       f"Available types are {results_df.columns.tolist()}\n"
                       f"Could there be a mismatch in locales?")

    # Then no true classes were found
    if detected_classes.shape[1] == 0:
        return None

    if not output_dict:
        filth_max_length = max([len(x[0]) for x in detected_columns] + [len("filth")])
        detector_name_max_length = max([len(x[1]) for x in detected_columns] + [len("detector")]) + 4
        locale_max_length = max([len(x[2]) for x in detected_columns] + [len("locale")]) + 4
        class_labels = [
            "{} {} {}  ".format(
                x[0].rjust(filth_max_length),
                x[1].rjust(detector_name_max_length),
                x[2].rjust(locale_max_length)
            )
            for x in detected_columns
        ]
    else:
        class_labels = ["{}:{}:{}".format(*x) for x in detected_columns]

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

    if not output_dict:
        report = (
            'filth'.rjust(filth_max_length) +
            'detector'.rjust(detector_name_max_length + 1) +
            'locale'.rjust(locale_max_length + 1) +
            (' '*4) +
            report.lstrip(' ')
        )
    return report


def get_filth_dataframe(filth_list: List[Filth]) -> pd.DataFrame:
    """Produces a pandas `DataFrame` to allow debugging and improving detectors.

    An example of using this is shown below:

    .. code:: pycon

        >>> import scrubadub, scrubadub.comparison, scrubadub.detectors.text_blob
        >>> scrubber = scrubadub.Scrubber(detector_list=[
        ...     scrubadub.detectors.TextBlobNameDetector(name='name_detector'),
        ...     scrubadub.detectors.KnownFilthDetector([
        ...         {'match': 'Tom', 'filth_type': 'name'},
        ...         {'match': 'tom@example.com', 'filth_type': 'email'},
        ...     ]),
        ... ])
        >>> filth_list = list(scrubber.iter_filth("Hello I am Tom"))
        >>> with pd.option_context("display.max_columns", 20):
        ...     print(scrubadub.comparison.get_filth_dataframe(filth_list))  # doctest: +NORMALIZE_WHITESPACE
           group_id  filth_id filth_type  detector_name document_name text  beg  end  \\
        0         0         0       name  name_detector          None  Tom   11   14
        <BLANKLINE>
          locale  known_filth comparison_type known_text  known_beg  known_end  \\
        0  en_US         True             NaN        Tom         11         14
        <BLANKLINE>
          known_comparison_type  exact_match  partial_match  true_positive  \\
        0                  name         True           True           True
        <BLANKLINE>
           false_positive  false_negative
        0           False           False

    :param filth_list: The list of detected filth
    :type filth_list: A list of `Filth` objects
    :return: A `pd.DataFrame` containing infomatoin about the detected `Filth`
    :rtype: `pd.DataFrame`

    """
    results = []
    for group_id, filth_item in enumerate(filth_list):
        sub_filths = [filth_item]
        if isinstance(filth_item, filth_module.base.MergedFilth):
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
                'locale': sub_filth.locale,
                'known_filth': isinstance(sub_filth, filth_module.KnownFilth),
                'comparison_type': getattr(sub_filth, 'comparison_type', float('nan')),
            })

    results_df = pd.DataFrame(results, columns=['group_id', 'filth_id', 'filth_type', 'detector_name', 'document_name',
                                                'text', 'beg', 'end', 'locale', 'known_filth', 'comparison_type'])
    suffix_label = '_y_suffix'

    return (
        pd.merge(
            results_df.loc[~results_df['known_filth']],
            results_df.loc[results_df['known_filth'], ['group_id', 'text', 'beg', 'end', 'comparison_type']],
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
        paragraphs: int = 20, locale: str = 'en_US', seed: Optional[int] = None, faker: Optional[Faker] = None,
        filth_types: Optional[List[str]] = None, fake_text_function: Optional[Callable] = None,
        additional_filth_types: Optional[List[Filth]] = None,
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

    :param paragraphs: The list of detected filth
    :type paragraphs: int
    :param locale: The locale of the documents in the format: 2 letter lower-case language code followed by an
                   underscore and the two letter upper-case country code, eg "en_GB" or "de_CH"
    :type locale: str
    :param seed: The random seed used to generate the document
    :type seed: int, optional
    :param faker: A Faker object that is used to generate the text
    :type faker: int
    :param filth_types: A list of the ``Filth.type`` to generate
    :type filth_types: List[str]
    :param fake_text_function: A function that will generate a 1-3 sentances of text
    :type fake_text_function: Callable, optional
    :return: The document and a list of `KnownFilthItem`\\ s
    :rtype: Tuple[str, List[KnownFilthItem]]

    """
    if faker is None:
        faker = Faker(locale=locale)

    if fake_text_function is None:
        fake_text_function = faker.text

    # TODO: register filth types to build up a dict that can be read from, like the detectors
    possible_filth = [
        filth_module.AddressFilth,
        filth_module.EmailFilth,
        filth_module.NameFilth,
        filth_module.PhoneFilth,
        filth_module.PostalCodeFilth,
        filth_module.SocialSecurityNumberFilth,
        filth_module.TwitterFilth,
        filth_module.UrlFilth,
    ]
    if additional_filth_types is not None:
        possible_filth += list(additional_filth_types)

    if filth_types is not None:
        possible_filth = [filth for filth in possible_filth if filth.type in filth_types]

    if seed is not None:
        Faker.seed(seed)
        random.seed(seed)

    doc = ""
    known_items = []  # type: List[KnownFilthItem]
    for i_paragraph in range(paragraphs):
        for i_sentance_group in range(random.randint(1, 10)):
            text = fake_text_function() + " "
            matches = list(re.finditer(r'[\s.]', text))
            position = random.choice(matches)
            chosen_filth = random.choice(possible_filth)
            pii_text = chosen_filth.generate(faker=faker)
            known_items.append({
                'match': copy.copy(pii_text),
                'filth_type': copy.copy(chosen_filth.type),
            })
            separator = position.group()
            if '\n' in pii_text:
                separator = '\n'
            doc += (
                text[:position.start()] +
                (separator if separator != '.' else separator + ' ') +
                pii_text +
                separator +
                text[position.end():]
            )
        doc += "\n\n"
    return (doc.strip(), known_items)
