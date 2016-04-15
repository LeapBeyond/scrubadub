import inspect
import glob
import os
import importlib


def _iter_package_module_names(package_root):
    init_filename = os.path.join(package_root, '__init__.py')
    for py_filename in sorted(glob.glob(os.path.join(package_root, '*.py'))):
        if py_filename != init_filename:
            filename_root, _ = os.path.splitext(py_filename)
            module_name = os.path.basename(filename_root)
            yield module_name


def _iter_module_subclasses(package, module_name, base_cls):
    """inspect all modules in this directory for subclasses of inherit from
    ``base_cls``. inpiration from http://stackoverflow.com/q/1796180/564709
    """
    module = importlib.import_module('.' + module_name, package)
    for name, obj in inspect.getmembers(module):
        if inspect.isclass(obj) and issubclass(obj, base_cls):
            yield obj


def iter_subclasses(package_root, base_cls, is_abstract):
    package = 'scrubadub.' + os.path.basename(package_root)
    for module_name in _iter_package_module_names(package_root):
        for cls in _iter_module_subclasses(package, module_name, base_cls):
            if not is_abstract(cls):
                yield cls


def update_locals(locals_instance, instance_iterator, *args, **kwargs):
    """import all of the detector classes into the local namespace to make it
    easy to do things like `import scrubadub.detectors.NameDetector` without
    having to add each new ``Detector`` or ``Filth``
    """
    # http://stackoverflow.com/a/4526709/564709
    # http://stackoverflow.com/a/511059/564709
    for instance in instance_iterator():
        locals_instance.update({type(instance).__name__: instance.__class__})
