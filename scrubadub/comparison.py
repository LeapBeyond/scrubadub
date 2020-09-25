
from . import filth
from .filth import Filth
from . import detectors

from typing import List, Dict, Union, Optional
import pandas as pd
import sklearn.metrics


def get_filth_classification_report(
        filth_list: List[filth.Filth],
        output_dict: bool = False,
) -> Optional[Union[str, Dict[str, float]]]:
    """Compares how much filth is detected by various detectors"""

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
    """Returns a dataframe with the """
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
                'detector_name': getattr(sub_filth, 'detector_name', pd.NA),
                'document_name': getattr(sub_filth, 'document_name', pd.NA),
                'text': sub_filth.text,
                'beg': sub_filth.beg,
                'end': sub_filth.end,
                'known_filth': isinstance(sub_filth, filth.KnownFilth),
                'comparison_type': getattr(sub_filth, 'comparison_type', pd.NA),
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
