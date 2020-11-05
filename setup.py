import glob
import os
from setuptools import setup

# read in the description from README
with open("README.rst") as stream:
    long_description = stream.read()

github_url = 'https://github.com/LeapBeyond/scrubadub'


def read_packages_from_file(filename):
    with open(filename, 'r') as stream:
        for line in stream:
            package = line.strip().split('#')[0]
            if package:
                yield package

# read in the dependencies from the virtualenv requirements file
filename = os.path.join("requirements", "python")
dependencies = list(read_packages_from_file(filename))

# read extra spacy dependencies from python-extras requirements file
filename = os.path.join("requirements", "python-extras")
extras = list(read_packages_from_file(filename))

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
        'scrubadub.post_processors',
        'scrubadub.post_processors.text_replacers',
    ],
    classifiers=[
        'Intended Audience :: Developers',
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Software Development :: Libraries',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Text Processing',
        'Topic :: Utilities',
    ],
    install_requires=dependencies,
    extras_require={"spacy": extras},
    zip_safe=False,
)
