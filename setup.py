import glob
import os
from setuptools import setup

import scrubadub

# read in the description from README
with open("README.rst") as stream:
    long_description = stream.read()

github_url='https://github.com/deanmalmgren/scrubadub'

# read in the dependencies from the virtualenv requirements file
dependencies = []
filename = os.path.join("requirements", "python")
with open(filename, 'r') as stream:
    for line in stream:
        package = line.strip().split('#')[0]
        if package:
            dependencies.append(package)

setup(
    name=scrubadub.__name__,
    version=scrubadub.VERSION,
    description="",
    long_description=long_description,
    url=github_url,
    download_url="%s/archives/master" % github_url,
    author='Dean Malmgren',
    author_email='dean.malmgren@datascopeanalytics.com',
    license='MIT',
    packages=[
        'scrubadub',
    ],
    install_requires=dependencies,
    zip_safe=False,
)
