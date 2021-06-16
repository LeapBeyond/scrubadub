import re
import copy
import random
import itertools

from faker import Faker

from . import filth as filth_module
from .filth import Filth
from .detectors.tagged import KnownFilthItem

from typing import List, Dict, Union, Optional, Tuple, Callable, Iterable, Type, Set
import numpy as np
import pandas as pd
import sklearn.metrics

# I was originally thinking of building this into the Filth system, but they serve subtlly different purposes:
#   * Filths need to be merged by text location so that replacements can be made
#   * TextPostions need to be merged by text location, but seperated by type so that we an correclty count them
from .utils import ToStringMixin

Grouping = Dict[str, str]
GroupingFunction = Callable[[Filth], Grouping]


class TextPosition(ToStringMixin):
    def __init__(self, filth: Filth, grouping_function: GroupingFunction):
        self.beg = filth.beg
        self.end = filth.end
        self.detected = set()  # type: Set[Tuple[str, ...]]
        self.tagged = set()  # type: Set[Tuple[str, ...]]
        self.document_name = str(filth.document_name or '')  # type: str

        if isinstance(filth, filth_module.TaggedEvaluationFilth):
            self.tagged.add(tuple(grouping_function(filth).values()))
        else:
            self.detected.add(tuple(grouping_function(filth).values()))

    @staticmethod
    def sort_key(position: 'TextPosition') -> Tuple[str, int, int]:
        return (position.document_name, position.beg, -position.end)

    def merge(self, other: 'TextPosition') -> 'TextPosition':
        if self.document_name != other.document_name:
            raise ValueError("Positions are in different documents")
        if self.beg <= other.end and self.end > other.beg:
            self.beg = min(self.beg, other.beg)
            self.end = max(self.end, other.end)
            self.tagged = self.tagged | other.tagged
            self.detected = self.detected | other.detected
            return self
        raise ValueError(f"Positions do not overlap {self.beg} to {self.end} and {other.beg} to {other.end}")

    def __repr__(self) -> str:
        return self._to_string(['beg', 'end', 'tagged', 'detected', 'document_name', ])

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


class FilthTypePositions(ToStringMixin, object):
    def __init__(self, grouping_function: GroupingFunction, filth_type: str):
        self.positions = []  # type: List[TextPosition]
        self.filth_type = filth_type
        self.grouping_function = grouping_function
        self.column_names = None  # type: Optional[List[str]]

    def __repr__(self) -> str:
        return self._to_string(['filth_type', 'positions', ])

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def add_filth(self, filth: Filth):
        self.positions.append(TextPosition(filth, grouping_function=self.grouping_function))
        if self.column_names is None:
            self.column_names = list(self.grouping_function(filth).keys())

    @staticmethod
    def _merge_position_list(position_list: List[TextPosition]) -> List[TextPosition]:
        position_list.sort(key=TextPosition.sort_key)
        merged_positions = []  # type: List[TextPosition]

        current_position = position_list[0]
        for next_position in position_list[1:]:
            if current_position.document_name != next_position.document_name or \
                    current_position.end <= next_position.beg:
                merged_positions.append(current_position)
                current_position = next_position
            else:
                current_position = current_position.merge(next_position)
        merged_positions.append(current_position)

        return merged_positions

    def merge_positions(self):
        self.positions = self._merge_position_list(self.positions)

    def get_counts(self) -> pd.DataFrame:
        self.merge_positions()

        data_list = []  # type: List[Dict[Tuple[str, ...], int]]
        for position in self.positions:
            row = {
                detected_name: 1
                for detected_name in position.detected
            }
            row.update({
                detected_name: 1
                for detected_name in position.tagged
            })
            data_list.append(row)

        dataframe = pd.DataFrame(data_list).fillna(0).astype(int)
        dataframe.columns = pd.MultiIndex.from_tuples(
            dataframe.columns.values.tolist(),
            names=self.column_names,
        )

        return dataframe


class FilthGrouper(ToStringMixin, object):
    def __init__(self, filth_types: Optional[List[str]] = None, grouping_function: Optional[GroupingFunction] = None,
                 combine_detectors: bool = False, groupby_documents: bool = False):
        self.types = {}  # type: Dict[str, FilthTypePositions]
        self.combine_detectors = combine_detectors
        self.groupby_documents = groupby_documents
        self.filth_types = filth_types

        if grouping_function is None:
            if self.combine_detectors and self.groupby_documents:
                self.grouping_function = FilthGrouper.grouping_combined_bydoc  # type: GroupingFunction
            elif self.combine_detectors and not self.groupby_documents:
                self.grouping_function = FilthGrouper.grouping_combined
            elif not self.combine_detectors and self.groupby_documents:
                self.grouping_function = FilthGrouper.grouping_default_bydoc
            else:
                self.grouping_function = FilthGrouper.grouping_default
        else:
            self.grouping_function = grouping_function

    def __repr__(self) -> str:
        return self._to_string(['combine_detectors', 'filth_types', 'types', ])

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    @staticmethod
    def grouping_default(filth: Filth) -> Grouping:
        detector_name = (
            (filth.detector_name or 'None')
            if not isinstance(filth, filth_module.TaggedEvaluationFilth) else
            filth_module.TaggedEvaluationFilth.type
        )
        result = {
            'filth': getattr(filth, 'comparison_type', filth.type),
            'detector': detector_name,
            'locale': filth.locale or 'None',
        }
        return result

    @staticmethod
    def grouping_default_bydoc(filth: Filth) -> Grouping:
        detector_name = (
            (filth.detector_name or 'None')
            if not isinstance(filth, filth_module.TaggedEvaluationFilth) else
            filth_module.TaggedEvaluationFilth.type
        )
        result = {
            'filth': getattr(filth, 'comparison_type', filth.type),
            'document_name': filth.document_name or 'None',
            'detector': detector_name,
            'locale': filth.locale or 'None',
        }

        return result

    @staticmethod
    def grouping_combined(filth: Filth) -> Grouping:
        detector_name = (
            'combined'
            if not isinstance(filth, filth_module.TaggedEvaluationFilth) else
            filth_module.TaggedEvaluationFilth.type
        )
        return {
            'filth': getattr(filth, 'comparison_type', filth.type),
            'detector': detector_name,
            'locale': filth.locale or 'None',
        }

    @staticmethod
    def grouping_combined_bydoc(filth: Filth) -> Grouping:
        detector_name = (
            'combined'
            if not isinstance(filth, filth_module.TaggedEvaluationFilth) else
            filth_module.TaggedEvaluationFilth.type
        )
        result = {
            'filth': getattr(filth, 'comparison_type', filth.type),
            'document_name': filth.document_name or 'None',
            'detector': detector_name,
            'locale': filth.locale or 'None',
        }

        return result

    def merge_positions(self):
        for positioniser in self.types.values():
            positioniser.merge_positions()

    def add_filths(self, filth_list: List[Filth]):
        for filth_item in filth_list:
            sub_filths = [filth_item]
            if isinstance(filth_item, filth_module.base.MergedFilth):
                sub_filths = filth_item.filths

            for filth in sub_filths:
                filth_type = (
                    filth.comparison_type if isinstance(filth, filth_module.TaggedEvaluationFilth) else filth.type
                )

                if filth_type is None or (self.filth_types is not None and filth_type not in self.filth_types):
                    continue

                if filth_type not in self.types:
                    self.types[filth_type] = FilthTypePositions(
                        filth_type=filth_type,
                        grouping_function=self.grouping_function
                    )

                self.types[filth_type].add_filth(filth)

    @classmethod
    def from_filth_list(
            cls, filth_list: List[Filth], filth_types: Optional[List[str]] = None,
            combine_detectors: bool = False, groupby_documents: bool = False,
            grouping_function: Optional[GroupingFunction] = None
    ) -> 'FilthGrouper':
        grouper = cls(filth_types=filth_types, combine_detectors=combine_detectors, groupby_documents=groupby_documents,
                      grouping_function=grouping_function)
        grouper.add_filths(filth_list)
        grouper.merge_positions()
        return grouper

    def expand_missing(self, df: pd.DataFrame) -> pd.DataFrame:
        set_list = [set(s) for s in zip(*df.columns.values.tolist())]
        for column in itertools.product(*set_list):
            if column not in df.columns:
                df.loc[:, column] = 0
        return df

    def get_counts(self, expand_missing: bool = False) -> pd.DataFrame:
        if len(self.types) == 0:
            return pd.DataFrame()
        df_list = []  # type: List[pd.DataFrame]
        running_rows = 0
        for positioniser in self.types.values():
            pos_df = positioniser.get_counts()
            if expand_missing:
                pos_df = self.expand_missing(pos_df)
            df_list.append(pos_df)
            df_list[-1].index += running_rows
            running_rows += max(df_list[-1].index) + 1
        return pd.concat(df_list).fillna(0).astype(int)


def get_filth_classification_report(
        filth_list: List[Filth],
        combine_detectors: bool = False,
        groupby_documents: bool = False,
        output_dict: bool = False,
) -> Optional[Union[str, Dict[str, float]]]:
    """Evaluates the performance of detectors using KnownFilth.

    An example of using this is shown below:

    .. code:: pycon

        >>> import scrubadub, scrubadub.comparison, scrubadub.detectors.text_blob
        >>> scrubber = scrubadub.Scrubber(detector_list=[
        ...     scrubadub.detectors.TextBlobNameDetector(name='name_detector'),
        ...     scrubadub.detectors.TaggedEvaluationFilthDetector([
        ...         {'match': 'Tom', 'filth_type': 'name'},
        ...         {'match': 'tom@example.com', 'filth_type': 'email'},
        ...     ]),
        ... ])
        >>> filth_list = list(scrubber.iter_filth("Hello I am Tom"))
        >>> print(scrubadub.comparison.get_filth_classification_report(filth_list))
        filth    detector         locale      precision    recall  f1-score   support
        <BLANKLINE>
        name     name_detector    en_US            1.00      1.00      1.00         1
        <BLANKLINE>
                                    accuracy                           1.00         1
                                   macro avg       1.00      1.00      1.00         1
                                weighted avg       1.00      1.00      1.00         1
        <BLANKLINE>

    :param filth_list: The list of detected filth
    :type filth_list: A list of `Filth` objects
    :param combine_detectors: Combine performance of all detectors for the same filth/locale
    :type combine_detectors: bool, optional
    :param groupby_documents: Show performance for each file individually
    :type groupby_documents: bool, optional
    :param output_dict: Return the report in JSON format, defautls to False
    :type output_dict: bool, optional
    :return: The report in JSON (a `dict`) or in plain text
    :rtype: `str` or `dict`
    """
    if len(filth_list) == 0:
        return None

    grouper = FilthGrouper.from_filth_list(filth_list, combine_detectors=combine_detectors,
                                           groupby_documents=groupby_documents)
    results_df = grouper.get_counts(expand_missing=True)

    filth_index = results_df.columns.names.index('filth')
    detector_index = results_df.columns.names.index('detector')
    tagged_column_mask = np.array(
        [x[detector_index] == filth_module.TaggedEvaluationFilth.type for x in results_df.columns]
    )

    # Find filth types that have some tagged filth
    tagged_types = [x[filth_index] for x in results_df.columns[tagged_column_mask]]

    # Select the columns that have some related tagged filth, but are not tagged filth themselves
    detected_columns = [
        x for x in results_df.columns[~tagged_column_mask]
        if x[filth_index] in tagged_types
    ]
    detected_classes = results_df.loc[:, detected_columns].values

    # Take the detected_columns above and find their tagged counterparts
    tagged_columns = [
        (*x[:detector_index], filth_module.TaggedEvaluationFilth.type, *x[detector_index + 1:])
        for x in detected_columns
    ]
    # If they don't have any tagged counterpart, set the column to zero
    for column in tagged_columns:
        if column not in results_df.columns:
            results_df.loc[:, column] = 0
            tagged_column_mask = np.append(tagged_column_mask, [True])

    true_classes = results_df.loc[:, tagged_columns].values

    # Then no true classes were found
    if detected_classes.shape[1] == 0:
        return None

    report_prefix = None  # type: Optional[str]
    if not output_dict:
        report_prefix = ''
        class_labels = [''] * len(detected_columns)
        for i, name in enumerate(results_df.columns.names):
            max_length = max([len(str(columns[i])) for columns in results_df.columns] + [len(name)]) + 4
            class_labels = [
                name + columns[i].ljust(max_length)
                for name, columns in zip(class_labels, detected_columns)
            ]
            report_prefix += name.ljust(max_length)
        class_labels = [
            name
            for name in class_labels
        ]
        if report_prefix is not None:
            report_prefix += '  '
    else:
        base_name = ("{}:" * len(results_df.columns.names)).rstrip(':')
        class_labels = [base_name.format(*x) for x in detected_columns]

    # If there is only one label reshape the data so that
    # the classification_report interprets it less ambiguously
    report_labels = []  # type: List[int]
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

    if report_prefix is not None:
        report = report_prefix + report.lstrip(' ')

    return report


def get_filth_dataframe(filth_list: List[Filth]) -> pd.DataFrame:
    """Produces a pandas `DataFrame` to allow debugging and improving detectors.

    An example of using this is shown below:

    .. code:: pycon

        >>> import scrubadub, scrubadub.comparison, scrubadub.detectors.text_blob
        >>> scrubber = scrubadub.Scrubber(detector_list=[
        ...     scrubadub.detectors.TextBlobNameDetector(name='name_detector'),
        ...     scrubadub.detectors.TaggedEvaluationFilthDetector([
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
                'known_filth': isinstance(sub_filth, filth_module.TaggedEvaluationFilth),
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
        filth_types: Optional[List[str]] = None, fake_text_function: Optional[Callable[..., str]] = None,
        additional_filth_types: Optional[Iterable[Type[Filth]]] = None,
) -> Tuple[str, List[KnownFilthItem]]:
    """Creates a fake document containing `Filth` that needs to be removed. Also returns the list of known filth
    items that are needed by the `TaggedEvaluationFilthDetector`\\ .

    An example of using this is shown below:

    .. code:: pycon

        >>> import scrubadub, scrubadub.comparison
        >>> document, known_filth_items = scrubadub.comparison.make_fake_document(paragraphs=1, seed=1)
        >>> scrubber = scrubadub.Scrubber()
        >>> scrubber.add_detector(scrubadub.detectors.TaggedEvaluationFilthDetector(
        ...     known_filth_items=known_filth_items
        ... ))
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
    for _ in range(paragraphs):
        for _ in range(random.randint(1, 10)):
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
