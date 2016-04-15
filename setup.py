import glob
import os
from setuptools import setup

# read in the description from README
with open("README.rst") as stream:
    long_description = stream.read()

github_url = 'https://github.com/datascopeanalytics/scrubadub'

# read in the dependencies from the virtualenv requirements file
dependencies = []
filename = os.path.join("requirements", "python")
with open(filename, 'r') as stream:
    for line in stream:
        package = line.strip().split('#')[0]
        if package:
            dependencies.append(package)

# get the version
version = None
with open(os.path.join('scrubadub', '__init__.py')) as stream:
    for line in stream:
        if 'version' in line.lower():
            version = line.split()[-1].replace('"', '').replace("'", '')

setup(
    name='scrubadub',
    version=version,
    description=(
        "Clean personally identifiable information from dirty dirty text."
    ),
    long_description=long_description,
    url=github_url,
    download_url="%s/archives/master" % github_url,
    author='Dean Malmgren',
    author_email='dean.malmgren@datascopeanalytics.com',
    license='MIT',
    packages=[
        'scrubadub',
        'scrubadub.filth',
        'scrubadub.detectors',
    ],
    install_requires=dependencies,
    zip_safe=False,
)
