#!/usr/bin/env python3

import os
import sys
import subprocess

from wasabi import msg

tests = [
    "mypy --config-file setup.cfg scrubadub/",
    "flake8  --config setup.cfg scrubadub/",
    # If py3.5 then examples with spacy don't work so disable doctests
    'if python3 --version | grep -Evq "Python (3\\.5\\.)" ; then nosetests --with-doctest --doctest-extension=rst ./tests/ ./scrubadub/ ./docs/ ; else nosetests ; fi',
    "python3 ./tests/benchmark_accuracy.py --fast",
    "python3 ./tests/benchmark_time.py",
    'if python3 --version | grep -Evq "Python (3\\.5\\.)" ; then cd docs && make html && cd - ; fi',
]


def run_test(command, directory):
    """Execute a command that runs a test"""
    msg.text("RUNNING  " + command)
    wrapped_command = f"cd {directory} && {command}"
    pipe = subprocess.Popen(
        wrapped_command, shell=True,
    )
    pipe.wait()
    if pipe.returncode == 0:
        msg.good("TEST PASSED")
    else:
        msg.fail("TEST FAILED")
    msg.text('')
    return pipe.returncode


root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# run the tests
if isinstance(tests, str):
    returncode = run_test(tests, root_dir)
elif isinstance(tests, (list, tuple)):
    returncode = 0
    for test in tests:
        returncode += run_test(test, root_dir)

if returncode == 0:
    msg.good("ALL TESTS PASSED")
else:
    msg.fail("SOME TESTS FAILED, SEE ABOVE")

sys.exit(returncode)
