import inspect
import glob
import os
import importlib


def _iter_module_names():
    this_filename = os.path.abspath(__file__)
    this_dir = os.path.dirname(this_filename)
    exclude_filenames = set((
        this_filename,
        this_filename.replace('.pyc', '.py'),
        os.path.join(this_dir, 'base.py'),
    ))
    for py_filename in sorted(glob.glob(os.path.join(this_dir, '*.py'))):
        if py_filename not in exclude_filenames:
            filename_root, _ = os.path.splitext(py_filename)
            module_name = os.path.basename(filename_root)
            yield module_name


# inspect all modules in this directory for subclasses of
# inherit from BaseRecommender. inpiration from
# http://stackoverflow.com/q/1796180/564709
def _get_detector(module_name):
    from .base import Detector, RegexDetector
    base_detectors = set([Detector, RegexDetector])
    module = importlib.import_module('.' + module_name, __package__)
    for name, obj in inspect.getmembers(module):
        if inspect.isclass(obj) and issubclass(obj, Detector) \
                and obj not in base_detectors:
            return obj


def iter_detector_clss():
    """Iterate over all of the detectors that are included in this sub-package.
    This is a convenience method for capturing all new Detectors that are added
    over time and it is used both by the unit tests and in the
    ``Scrubber.__init__`` method.
    """
    for module_name in _iter_module_names():
        detector_cls = _get_detector(module_name)
        if detector_cls is not None:
            yield detector_cls


# import all of the detector classes into the local namespace to make it easy
# to do things like `import scrubadub.detectors.NameDetector`
# http://stackoverflow.com/a/4526709/564709
# http://stackoverflow.com/a/511059/564709
for _detector_cls in iter_detector_clss():
    locals().update({type(_detector_cls()).__name__: _detector_cls})
