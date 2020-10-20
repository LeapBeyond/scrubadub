#!/usr/bin/env python

"""Run the test suite that is specified in the .travis.yml file
"""

import os
import sys
import subprocess

import yaml
from colors import green, red


def run_test(command, directory):
    """Execute a command that runs a test"""
    wrapped_command = "cd %s && %s" % (directory, command)
    pipe = subprocess.Popen(
        wrapped_command, shell=True,
    )
    pipe.wait()
    if pipe.returncode == 0:
        print(green("TEST PASSED"))
    else:
        print(red("TEST FAILED"))
    return pipe.returncode


root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# load the script tests from the .travis.yml file
with open(os.path.join(root_dir, '.travis.yml')) as stream:
    travis_yml = yaml.safe_load(stream.read())
tests = travis_yml['script']

# run the tests
if isinstance(tests, str):
    returncode = run_test(tests, root_dir)
elif isinstance(tests, (list, tuple)):
    returncode = 0
    for test in tests:
        returncode += run_test(test, root_dir)

if returncode == 0:
    print(green("ALL TESTS PASSED"))
else:
    print(red("SOME TESTS FAILED, SEE ABOVE"))

sys.exit(returncode)
