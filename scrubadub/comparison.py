
from . import filth
from . import detectors

import typing
import numpy as np
import inspect


def compare_detectors(
        filth_list: typing.List[filth.Filth],
        detector_list: typing.List[detectors.Detector]
) -> typing.Dict[str, float]:
    """Compares how much filth is detected by various detectors"""
    results = []
    filth_classes = [det.filth_cls for det in detector_list]

    for filth_item in filth_list:
        sub_filths = [filth_item]
        if isinstance(filth_item, filth.base.MergedFilth):
            sub_filths = filth_item.filths

        # print(isinstance(sub_filths[0], filth_classes[0]), sub_filths[0], filth_classes[0])
        # print(isinstance(sub_filths[0], filth_classes[1]), sub_filths[0], filth_classes[1])
        # print(isinstance(sub_filths[1], filth_classes[0]), sub_filths[1], filth_classes[0])
        # print(isinstance(sub_filths[1], filth_classes[1]), sub_filths[1], filth_classes[1])

        filth_class_result = [
            float(any([isinstance(sub_filth, filth_cls) for sub_filth in sub_filths]))
            for filth_cls in filth_classes
        ]
        # print(filth_class_result)
        # Dont include filth that was not produced by one
        # of the detectors of interest
        if sum(filth_class_result) > 0:
            results.append(filth_class_result)

    if len(results) == 0:
        return {}

    detection_rate = np.array(results).mean(axis=0).tolist()
    return {
        key: value
        for key, value in zip(
            [filth_cls.type for filth_cls in filth_classes],
            detection_rate
        )
    }
