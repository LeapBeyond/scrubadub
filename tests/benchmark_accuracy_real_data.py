#!/usr/bin/env python3

import os
import io
import time
import glob
import click
import dotenv
# import chardet
# try a new chardet package, its a drop in replacement based on a mozilla project.
import cchardet as chardet
import logging
import posixpath
import azure.storage.blob

from typing import List, Union, Sequence, Optional, Dict
from urllib.parse import urlparse

import scrubadub
from scrubadub.comparison import get_filth_classification_report, KnownFilthItem, get_filth_dataframe
from scrubadub.filth.base import Filth


def get_blob_service(connection_string: Optional[str] = None) -> azure.storage.blob.BlobServiceClient:
    if connection_string is None:
        connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")

    if connection_string is None:
        env_path = None
        env_paths = ["./.env", "../.env"]
        for path in env_paths:
            if os.path.exists(path):
                env_path = path

        dotenv.load_dotenv(dotenv_path=env_path)
        connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")

    if connection_string is None:
        message = "Environment variable AZURE_STORAGE_CONNECTION_STRING needs to be set. "
        raise EnvironmentError(message)

    import azure.storage.blob
    blob_service_client = azure.storage.blob.BlobServiceClient.from_connection_string(conn_str=connection_string)

    return blob_service_client


def load_local_files(path: str) -> Dict[str, bytes]:
    files = {}
    for file_name in glob.glob(path):
        with open(file_name, 'rb') as f:
            files[file_name] = f.read()

    if len(files) == 0:
        raise FileNotFoundError("Unable to find {}".format(path))

    return files


def load_azure_files(url: str, storage_connection_string: Optional[str] = None) -> Dict[str, bytes]:
    parsed_url = urlparse(url)
    container_split = parsed_url.netloc.split('.')
    try:
        account = ".".join(container_split[:container_split.index('blob')])
    except (ValueError, IndexError):
        raise click.UsageError(
            "Unable to determine the account from {}. The URL should be in the format: "
            "\n    https://{{ACCOUNT}}.blob.core.windows.net/{{CONTAINER}}/{{BLOB}}".format(parsed_url.netloc)
        )
    blob_service_client = get_blob_service(connection_string=storage_connection_string)
    if account != blob_service_client.account_name:
        raise click.UsageError(
            "Your credentials are for account '{account}' and so your URL should be in the form: "
            "\n    https://{account}.blob.core.windows.net/{{CONTAINER}}/{{BLOB}}".format(
                account=blob_service_client.account_name
            )
        )

    path, container = parsed_url.path, parsed_url.path
    while path not in ('/', ''):
        path, container = posixpath.split(path)
    path = parsed_url.path[len(container)+2:]

    container_client = blob_service_client.get_container_client(container)
    file_names = [
        blob.name
        for blob in list(container_client.list_blobs(path))
    ]

    file_content = {}
    for file_name in file_names:
        blob_client = blob_service_client.get_blob_client(blob=file_name, container=container)
        file_content[file_name] = blob_client.download_blob().readall()

    return file_content


def decode_text(documents: Dict[str, bytes]) -> Dict[str, str]:
    decoded_documents = {}  # type: Dict[str, str]
    for name, value in documents.items():
        text = ""
        charset = chardet.detect(value)
        encoding = charset.get('encoding', 'utf-8')

        # Try the auto-detected encoding first  then try some common ones
        for test_encoding in [encoding, 'utf-8', 'ISO-8859-1', 'windows-1251', 'windows-1252', 'utf-16']:
            if test_encoding is None:
                continue
            try:
                text = value.decode(test_encoding)
            except UnicodeDecodeError:
                pass
            else:
                encoding = test_encoding
                break

        # If the decoded text is blank, but the encoded text isn't blank
        if len(text) == 0 and len(value) > 0:
            logger = logging.getLogger('scrubadub.tests.benchmark_accuracy_real_data')
            logger.warning("Skipping file, unable to decode: {} (detected {})".format(name, encoding))
            continue

        decoded_documents[name] = text

    return decoded_documents


def load_files(path: str, storage_connection_string: Optional[str] = None) -> Dict[str, bytes]:
    if path.startswith('https://') or path.startswith('http://'):
        parsed_url = urlparse(path)
        if parsed_url.netloc.endswith('blob.core.windows.net'):
            return load_azure_files(path, storage_connection_string=storage_connection_string)
        else:
            raise NotImplementedError('Only azure blob storage URLs are currently supported.')

    return load_local_files(path)


def load_known_pii(known_pii_locations: List[str],
                   storage_connection_string: Optional[str] = None) -> List[KnownFilthItem]:
    start_time = time.time()
    click.echo("Loading Known Filth...")

    import pandas as pd
    known_pii = []

    for known_pii_location in known_pii_locations:
        file_data = load_files(known_pii_location, storage_connection_string=storage_connection_string)
        for file_name, data in file_data.items():
            dataframe = pd.read_csv(io.BytesIO(data), dtype={'match': str, 'match_end': str})
            known_pii += dataframe.to_dict(orient='records')
            if sorted(dataframe.columns.to_list()) != sorted(['match', 'match_end', 'limit', 'filth_type']):
                raise ValueError(
                    "Unexpected columns in '{}'. Expected the following columns: match, match_end, limit and "
                    "filth_type".format(file_name)
                )
            if pd.isnull(dataframe['match']).sum() > 0:
                raise ValueError(
                    "The KnownFilth column 'match' contains some null/blank entries in '{}'".format(file_name)
                )
            if pd.isnull(dataframe['filth_type']).sum() > 0:
                raise ValueError(
                    "The KnownFilth column 'filth_type' contains some null/blank entries in '{}'".format(file_name)
                )

    for item in known_pii:
        for sub_item in ('limit', 'match_end'):
            if pd.isnull(item[sub_item]):
                del item[sub_item]

    end_time = time.time()
    click.echo("Loaded Known Filth in {:.2f}s".format(end_time-start_time))

    return known_pii


def load_documents(document_locations: List[str], storage_connection_string: Optional[str] = None) -> Dict[str, str]:
    start_time = time.time()
    click.echo("Loading documents...")
    documents = {}  # type: Dict[str, str]

    for document_location in document_locations:
        binary_data = load_files(document_location, storage_connection_string=storage_connection_string)
        text_data = decode_text(binary_data)
        if len(set(documents.keys()).intersection(set(text_data.keys()))) > 0:
            raise ValueError('The same file has been repeated twice')
        documents.update(text_data)

    end_time = time.time()
    click.echo("Loaded documents in {:.2f}s".format(end_time-start_time))

    return documents


def scrub_documents(documents: Dict[str, str], known_filth_items: List[KnownFilthItem], locale: str) -> List[Filth]:
    start_time = time.time()
    click.echo("Initialising scrubadub...")
    scrubber = scrubadub.Scrubber(locale=locale)
    scrubber.add_detector(scrubadub.detectors.KnownFilthDetector(locale=locale, known_filth_items=known_filth_items))
    end_time = time.time()
    click.echo("Initialised scrubadub {:.2f}s".format(end_time-start_time))

    start_time = time.time()
    click.echo("Scrubbing {} documents".format(len(documents)))
    found_filth = list(scrubber.iter_filth_documents(documents))
    end_time = time.time()
    click.echo("Scrubbed documents in {:.2f}s".format(end_time-start_time))

    return found_filth


def load_complicated_detectors() -> Dict[str, bool]:
    detector_available = {
        'address': False,
        'spacy': False,
        'stanford': False,
        'text_blob': False,
    }

    try:
        import scrubadub.detectors.stanford
        detector_name = scrubadub.detectors.stanford.StanfordEntityDetector.name
        scrubadub.detectors.detector_configuration[detector_name]['autoload'] = True
        detector_available['stanford'] = True
    except ImportError:
        pass
    try:
        import scrubadub.detectors.address
        detector_name = scrubadub.detectors.address.AddressDetector.name
        scrubadub.detectors.detector_configuration[detector_name]['autoload'] = True
        detector_available['address'] = True
    except ImportError:
        pass
    # try:
    #     import scrubadub.detectors.text_blob
    #     detector_name = scrubadub.detectors.text_blob.TextBlobNameDetector.name
    #     scrubadub.detectors.detector_configuration[detector_name]['autoload'] = True
    #     detector_available['text_blob'] = True
    # except ImportError:
    #     pass
    try:
        import scrubadub.detectors.spacy
        detector_available['spacy'] = True
    except ImportError:
        pass
    if detector_available['spacy']:
        del scrubadub.detectors.detector_configuration[scrubadub.detectors.spacy.SpacyEntityDetector.name]

        # TODO: this only supports english models for spacy, this should be improved
        class SpacyEnSmDetector(scrubadub.detectors.spacy.SpacyEntityDetector):
            name = 'spacy_en_core_web_sm'
            def __init__(self, **kwargs):
                super(SpacyEnSmDetector, self).__init__(model='en_core_web_sm', **kwargs)

        class SpacyEnMdDetector(scrubadub.detectors.spacy.SpacyEntityDetector):
            name = 'spacy_en_core_web_md'
            def __init__(self, **kwargs):
                super(SpacyEnMdDetector, self).__init__(model='en_core_web_md', **kwargs)

        class SpacyEnLgDetector(scrubadub.detectors.spacy.SpacyEntityDetector):
            name = 'spacy_en_core_web_lg'
            def __init__(self, **kwargs):
                super(SpacyEnLgDetector, self).__init__(model='en_core_web_lg', **kwargs)

        class SpacyEnTrfDetector(scrubadub.detectors.spacy.SpacyEntityDetector):
            name = 'spacy_en_core_web_trf'
            def __init__(self, **kwargs):
                super(SpacyEnTrfDetector, self).__init__(model='en_core_web_trf', **kwargs)

        scrubadub.detectors.register_detector(SpacyEnSmDetector, autoload=True)
        scrubadub.detectors.register_detector(SpacyEnMdDetector, autoload=True)
        scrubadub.detectors.register_detector(SpacyEnLgDetector, autoload=True)
        scrubadub.detectors.register_detector(SpacyEnTrfDetector, autoload=True)

    return detector_available


def create_filth_summaries(found_filth: List[Filth], filth_matching_dataset: Optional[click.utils.LazyFile],
                           filth_matching_report: Optional[click.utils.LazyFile]):
    if filth_matching_dataset is None and filth_matching_report is None:
        return None

    dataframe = get_filth_dataframe(found_filth)

    if filth_matching_dataset is not None:
        dataframe.to_csv(filth_matching_dataset)

    if filth_matching_report is not None:
        with open(filth_matching_report.name, mode='wt') as report_file:
            dataframe['filth_type'] = dataframe['filth_type'].fillna(dataframe['known_comparison_type'])
            filth_types = dataframe['filth_type'].dropna().unique()
            report_file.write('# Filth summary report\n')
            for filth_type in filth_types:
                report_file.write('\n## {} filth\n'.format(filth_type))
                frequent = (
                    dataframe
                    [(dataframe['filth_type'] == filth_type) & ~dataframe['text'].isnull()]
                    ['text']
                    .value_counts()
                    .head(10)
                )
                frequent.index.name = 'text'
                frequent.name = 'count'

                false_positive = (
                    dataframe
                    [(dataframe['filth_type'] == filth_type) & dataframe['false_positive']]
                    [['document_name', 'detector_name', 'text', 'false_positive']]
                    .drop_duplicates()
                )
                false_positive.index.name = 'index'

                false_negative = (
                    dataframe
                    [(dataframe['filth_type'] == filth_type) & dataframe['false_negative']]
                    [['known_text', 'false_negative']]
                    .drop_duplicates()
                )
                false_negative.index.name = 'index'

                if false_positive.shape[0] > 10:
                    false_positive = false_positive.sample(10)
                if false_negative.shape[0] > 10:
                    false_negative = false_negative.sample(10)

                report_file.write(
                    "\n### Most frequent {}\n\n{}\n".format(filth_type, frequent.to_markdown())
                )
                report_file.write(
                    "\n### Sample of {} false positives\n\n{}\n".format(filth_type, false_positive.to_markdown())
                )
                report_file.write(
                    "\n### Sample of {} false negatives\n\n{}\n".format(filth_type, false_negative.to_markdown())
                )


def not_none_argument(ctx, param, value):
    error = click.BadParameter('This parameter is required, please set a value.')
    if value is None:
        raise error
    if len(value) == 0:
        raise error

    return value


@click.command()
@click.option('--fast', is_flag=True, help='Only run fast detectors')
@click.option('--locale', default='en_GB', show_default=True, metavar='<locale>', type=str,
              help='Locale to run with')
@click.option('--storage-connection-string', type=str, envvar='AZURE_STORAGE_CONNECTION_STRING', metavar='<string>',
              help='Connection string to azure bob storage (if needed)')
@click.option('--known-pii', type=str, multiple=True, metavar='<file>', help="File containing known PII CSV",
              callback=not_none_argument)
@click.option('--filth-matching-dataset', type=click.File('wt'),
              help="Location of csv file to save detailed matching information to")
@click.option('--filth-matching-report', type=click.File('wt'),
              help="Location of markdown file to save matching report to")
@click.option('--debug-log', type=click.File('wt'),
              help="Location of a log file for log messages that may contain PII")
@click.argument('document', metavar='DOCUMENT', type=str, nargs=-1, callback=not_none_argument)
def main(document: Union[str, Sequence[str]], fast: bool, locale: str, storage_connection_string: Optional[str],
         known_pii: Sequence[str], filth_matching_dataset: Optional[click.utils.LazyFile],
         filth_matching_report: Optional[click.utils.LazyFile], debug_log: Optional[click.utils.LazyFile]):
    """Test scrubadub accuracy using text DOCUMENT(s). Requires a CSV of known PII.

    DOCUMENT(s) can be specified as local paths or azure blob storage URLs in the form:
        https://{{ACCOUNT}}.blob.core.windows.net/{{CONTAINER}}/{{BLOB}}

    \b
    CSV containing known PII should be in the following format:
        filth_type,match,match_end,limit
        address,123 The Street,England,
        phone,077722122121,,
    See example in ./example_real_data/

    \b
    Example usage:
        $ ./benchmark_accuracy_real_data.py --locale en_GB --known-pii ./example_real_data/known_pii.csv ./example_real_data/document.txt
    """

    run_slow = not fast
    if run_slow:
        load_complicated_detectors()

    # Setup a logger that we can use to log things with possible PII data in that won't go to stdout
    logger = logging.getLogger('scrubadub')
    logger.handlers = []
    logger.setLevel(logging.NOTSET)

    if debug_log is not None:
        root_logger = logging.getLogger()
        root_logger.removeHandler(root_logger.handlers[0])
        root_logger.setLevel(logging.WARNING)

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler = logging.FileHandler(debug_log.name, mode='wt')
        file_handler.setFormatter(formatter)

        root_logger.addHandler(file_handler)

    known_pii_locations = list(known_pii)
    known_filth_items = load_known_pii(
        known_pii_locations=known_pii_locations, storage_connection_string=storage_connection_string
    )

    documents_list = list(document)
    documents = load_documents(
        document_locations=documents_list, storage_connection_string=storage_connection_string
    )

    found_filth = scrub_documents(documents=documents, known_filth_items=known_filth_items, locale=locale)

    create_filth_summaries(found_filth, filth_matching_dataset, filth_matching_report)

    classification_report = get_filth_classification_report(found_filth)
    if classification_report is None:
        click.echo("WARNING: No Known Filth was found in the provided documents.")
        return

    click.echo("\n" + classification_report)

    classification_report = get_filth_classification_report(found_filth, combine_detectors=True)
    if classification_report is None:
        click.echo("ERROR: Combined classification report is None.")
        return


if __name__ == "__main__":
    main()
