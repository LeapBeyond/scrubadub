"""
This module provides a detector to detect people's names using the Stanford CRF NER tagger.

See https://nlp.stanford.edu/software/CRF-NER.html for more details on the Stanford CRF NER Tagger

This detector requires java and the python package `nltk`.
The Stanford CRF NER Tagger will be downloaded to `~/.scrubadub/stanford_ner` and takes around 250MB.
"""
import re
import os
import pathlib
import zipfile
import requests
try:
    import nltk
except ImportError:
    raise ImportError(
        'To use scrubadub.detectors.stanford extra dependencies need to be installed.\n'
        'Please run: pip install scrubadub[stanford]'
    )

from typing import Dict, Type, Optional, List

from . import register_detector
from .base import Detector
from ..filth.base import Filth
from ..filth.name import NameFilth
from ..filth.organization import OrganizationFilth
from ..filth.location import LocationFilth


class ScrubadubStanfordNERTagger(nltk.tag.StanfordNERTagger):
    """Utility class to control options that the StanfordNERTagger is run with"""
    @property
    def _cmd(self):
        return [
            "edu.stanford.nlp.ie.crf.CRFClassifier",
            "-loadClassifier",
            self._stanford_model,
            "-textFile",
            self._input_file_path,
            "-outputFormat",
            self._FORMAT,
            "-tokenizerFactory",
            "edu.stanford.nlp.process.WhitespaceTokenizer",
            "-tokenizerOptions",
            '"tokenizeNLs=false"',
            '-nthreads',
            '1',
        ]


class StanfordEntityDetector(Detector):
    """Search for people's names, organization's names and locations within text using the stanford 3 class model.

    The three classes of this model can be enabled with the three arguments to the inialiser `enable_person`,
    `enable_organization` and `enable_location`.
    An example of their usage is given below.

    >>> import scrubadub, scrubadub.detectors.stanford
    >>> detector = scrubadub.detectors.StanfordEntityDetector(
    ...     enable_person=False, enable_organization=False, enable_location=True
    ... )
    >>> scrubber = scrubadub.Scrubber(detector_list=[detector])
    >>> scrubber.clean('Jane is visiting London.')
    'Jane is visiting {{LOCATION}}.'
    """
    filth_cls = Filth
    name = "stanford"
    ignored_words = ["tennant"]

    # TODO: NER model Has been wrapped into coreNLP packagewhich has version 4.1.0 out now.
    #  The download script needs to be updated.
    # TODO: Add support for Spanish, German, Chinese, French (No Arabic NER model)
    stanford_version = "4.0.0"
    stanford_download_url = 'https://nlp.stanford.edu/software/stanford-ner-{version}.zip'

    def __init__(self, enable_person: bool = True, enable_organization: bool = True, enable_location: bool = False,
                 **kwargs):
        """Initialise the ``Detector``.

        :param name: Overrides the default name of the :class:``Detector``
        :type name: str, optional
        :param locale: The locale of the documents in the format: 2 letter lower-case language code followed by an
                       underscore and the two letter upper-case country code, eg "en_GB" or "de_CH".
        :type locale: str, optional
        """
        self.stanford_tagger = None  # type: Optional[nltk.tag.StanfordNERTagger]

        self.filth_lookup = {}  # type: Dict[str, Type[Filth]]
        if enable_person:
            self.filth_lookup['PERSON'] = NameFilth
        if enable_organization:
            self.filth_lookup['ORGANIZATION'] = OrganizationFilth
        if enable_location:
            self.filth_lookup['LOCATION'] = LocationFilth

        self.stanford_classifier = os.path.join('stanford-ner-{version}', 'classifiers',
                                                'english.all.3class.distsim.crf.ser.gz')

        self.stanford_prefix = pathlib.Path.home().joinpath('.scrubadub').joinpath('stanford_ner').__str__()
        self.stanford_download_path = os.path.join(self.stanford_prefix, 'stanford-ner-{version}.zip')
        self.stanford_classifier_path = os.path.join(self.stanford_prefix, self.stanford_classifier)
        self.stanford_ner_jar_path = os.path.join(self.stanford_prefix, 'stanford-ner-{version}', 'stanford-ner.jar')

        self.stanford_files = [
            self.stanford_classifier,
            os.path.join('stanford-ner-{version}', 'stanford-ner.jar'),
            os.path.join('stanford-ner-{version}', 'stanford-ner-{version}.jar'),
            os.path.join('stanford-ner-{version}', 'stanford-ner-{version}-javadoc.jar'),
            os.path.join('stanford-ner-{version}', 'stanford-ner-{version}-sources.jar'),
        ]

        super(StanfordEntityDetector, self).__init__(**kwargs)

    def _check_downloaded(self):
        """Find out if the stanford NER tagger has already been downloaded"""
        paths = [
            os.path.join(self.stanford_prefix, file_name.format(version=self.stanford_version))
            for file_name in self.stanford_files
        ]
        for file_path in paths:
            if not os.path.exists(file_path):
                return False
        return True

    def _download(self):
        """Download and extract the eneeded files from the Stanford NER tagger"""
        # Make the data directory
        pathlib.Path(self.stanford_prefix).mkdir(parents=True, exist_ok=True)

        # Download the NER tagger
        download_path = self.stanford_download_path.format(version=self.stanford_version)
        if not pathlib.Path(download_path).exists():
            download_request = requests.get(self.stanford_download_url.format(version=self.stanford_version))
            with open(download_path, 'wb') as download_file:
                download_file.write(download_request.content)

        # Extract the needed files
        with zipfile.ZipFile(download_path, 'r') as downloaded_zip_file:
            for file_to_extract in self.stanford_files:
                downloaded_zip_file.extract(
                    member=file_to_extract.format(version=self.stanford_version),
                    path=self.stanford_prefix
                )

        # Ensure it extracted the files that we need
        if not self._check_downloaded():
            raise RuntimeError(
                "Unable to download the Stanford NER tagger from {url}, perhaps try again?".format(
                    url=self.stanford_download_url
                )
            )

    def iter_filth(self, text, document_name: Optional[str] = None):
        """Yields discovered filth in the provided ``text``.

        :param text: The dirty text to clean.
        :type text: str
        :param document_name: The name of the document to clean.
        :type document_name: str, optional
        :return: An iterator to the discovered :class:`Filth`
        :rtype: Iterator[:class:`Filth`]
        """
        if self.stanford_tagger is None:
            if not self._check_downloaded():
                self._download()

            self.stanford_tagger = ScrubadubStanfordNERTagger(
                self.stanford_classifier_path.format(version=self.stanford_version),
                self.stanford_ner_jar_path.format(version=self.stanford_version),
            )

        tokens = nltk.tokenize.word_tokenize(text)
        tags = self.stanford_tagger.tag(tokens)

        grouped_tags = {}  # type: Dict[str, List[str]]
        previous_tag = None

        # Loop over all tagged words and join contiguous words tagged as people
        for tag_text, tag_type in tags:
            if tag_type in self.filth_lookup.keys() and not any(
                    [tag_text.lower().strip() == ignored.lower().strip() for ignored in self.ignored_words]):
                if previous_tag == tag_type:
                    grouped_tags[tag_type][-1] = grouped_tags[tag_type][-1] + ' ' + tag_text
                else:
                    grouped_tags[tag_type] = grouped_tags.get(tag_type, []) + [tag_text]

                previous_tag = tag_type
            else:
                previous_tag = None

        # for each set of tags, de-dupe and convert to regex
        for tag_type, tag_list in grouped_tags.items():
            grouped_tags[tag_type] = [
                r'\b' + re.escape(person).replace(r'\ ', r'\s+') + r'\b'
                for person in set(tag_list)
            ]

        # Now look for these in the original document
        for tag_type, tag_list in grouped_tags.items():
            for tag_regex in tag_list:
                try:
                    pattern = re.compile(tag_regex, re.MULTILINE | re.UNICODE)
                except re.error:
                    print(tag_regex)
                    raise
                found_strings = re.finditer(pattern, text)

                # Iterate over each found string matching this regex and yield some filth
                for instance in found_strings:
                    yield self.filth_lookup[tag_type](
                        beg=instance.start(),
                        end=instance.end(),
                        text=instance.group(),
                        detector_name=self.name,
                        document_name=document_name,
                        locale=self.locale,
                    )

    @classmethod
    def supported_locale(cls, locale: str) -> bool:
        """Returns true if this ``Detector`` supports the given locale.

        :param locale: The locale of the documents in the format: 2 letter lower-case language code followed by an
                       underscore and the two letter upper-case country code, eg "en_GB" or "de_CH".
        :type locale: str
        :return: ``True`` if the locale is supported, otherwise ``False``
        :rtype: bool
        """
        language, region = cls.locale_split(locale)
        return language in ['en']


register_detector(StanfordEntityDetector, autoload=False)

__all__ = ["StanfordEntityDetector"]
