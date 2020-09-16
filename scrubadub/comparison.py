
from . import filth
from . import detectors

import typing
import pandas as pd
import sklearn.metrics


def compare_detectors_to_known_types(
        filth_list: typing.List[filth.Filth],
        detector_list: typing.List[detectors.Detector],
        output_dict: bool = False,
) -> typing.Dict[str, float]:
    """Compares how much filth is detected by various detectors"""
    results = []  # type: List[List[float]]
    filth_types = [det.filth_cls.type for det in detector_list]  # type: List[str]
    if filth.KnownFilth.type in filth_types:
        filth_types.pop(filth_types.index(filth.KnownFilth.type))

    filth_types_to_search = [(t, None) for t in filth_types]  # type: List[Tuple[str, Optional[str]]]
    filth_types_to_search += [(filth.KnownFilth.type, t[0]) for t in filth_types_to_search]

    for filth_item in filth_list:
        sub_filths = [filth_item]
        if isinstance(filth_item, filth.base.MergedFilth):
            sub_filths = filth_item.filths

        filth_contains_classes = []
        for filth_type_to_match, comparison_type_to_match in filth_types_to_search:
            found_type_in_sub_filths = False
            for sub_filth in sub_filths:
                # If we found a predefined sub_filth and it specifies a comparison type, then we
                # also require that this matches the filth class.
                if isinstance(sub_filth, filth.KnownFilth) and sub_filth.comparison_type is not None:
                    found_type_in_sub_filths |= (
                        sub_filth.type == filth_type_to_match and
                        sub_filth.comparison_type == comparison_type_to_match
                    )
                else:
                    found_type_in_sub_filths |= (sub_filth.type == filth_type_to_match)
            filth_contains_classes.append(float(found_type_in_sub_filths))
        # Dont include filth that was not produced by one of the detectors of interest
        if sum(filth_contains_classes) > 0:
            results.append(filth_contains_classes)

    if len(results) == 0:
        return {}

    results_df = pd.DataFrame(results, columns=pd.MultiIndex.from_tuples(filth_types_to_search))

    detected_classes = results_df.loc[:, [x for x in results_df.columns if x[0] != filth.KnownFilth.type]].values
    true_classes = results_df.loc[:, [x for x in results_df.columns if x[0] == filth.KnownFilth.type]].values

    extra_args = {}
    # If there is only one label reshape the data so that
    # the classification_report interprets it less ambiguously
    if detected_classes.shape[1] == 1:
        detected_classes = detected_classes.T[0]
        true_classes = true_classes.T[0]
        extra_args['labels'] = [1]

    report = sklearn.metrics.classification_report(
        true_classes,
        detected_classes,
        output_dict=output_dict,
        zero_division=0,
        target_names=[x[0] for x in results_df.columns if x[0] != filth.KnownFilth.type],
        **extra_args
    )
    return report
