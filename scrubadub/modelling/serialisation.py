import importlib
import json

import numpy as np
from sklearn.base import BaseEstimator


def estimator_to_json(estimator: BaseEstimator, file_path: str) -> None:
    type_dict_ = {}
    data_dict_ = {}
    for item_name, item in estimator.__dict__.items():
        if isinstance(item, type) and item.__module__ == 'numpy':
            data_dict_[item_name] = item.__name__
            type_dict_[item_name] = 'np.type'
        elif isinstance(item, np.dtype):
            data_dict_[item_name] = str(item)
            type_dict_[item_name] = 'dtype'
        elif isinstance(item, np.ndarray):
            data_dict_[item_name] = item.tolist()
            type_dict_[item_name] = str(item.dtype)
        else:
            data_dict_[item_name] = item

    dict_ = {
        'type_name': type(estimator).__name__,
        'type_module': type(estimator).__module__,
        'types': type_dict_,
        'data': data_dict_,
    }

    json_txt = json.dumps(dict_, indent=4)
    with open(file_path, 'w') as file:
        file.write(json_txt)


def estimator_from_json(file_path: str) -> BaseEstimator:
    with open(file_path, 'r') as file:
        dict_ = json.load(file)

    cls = importlib.import_module(dict_['type_module']).__getattribute__(dict_['type_name'])
    new_obj = cls()
    for item_name, saved_item in dict_['data'].items():
        if isinstance(saved_item, str) and item_name in dict_['types'] and dict_['types'][item_name] == 'np.type':
            new_obj.__setattr__(item_name, np.__getattribute__(saved_item))
        elif isinstance(saved_item, str) and item_name in dict_['types'] and dict_['types'][item_name] == 'dtype':
            new_obj.__setattr__(item_name, np.dtype(saved_item))
        elif isinstance(saved_item, list) and item_name in dict_['types']:
            new_obj.__setattr__(item_name, np.array(saved_item, dtype=dict_['types'][item_name]))
        else:
            new_obj.__setattr__(item_name, saved_item)

    return new_obj
