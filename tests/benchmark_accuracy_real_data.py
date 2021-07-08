#!/usr/bin/env python3

import os
import io
import time
import glob
import click
import magic
import dotenv
# import chardet
# try a new chardet package, its a drop in replacement based on a mozilla project.
import cchardet as chardet
import logging
import posixpath
import azure.storage.blob

from pandas import DataFrame

from typing import List, Union, Sequence, Optional, Dict, Any
from urllib.parse import urlparse, unquote

import scrubadub
import scrubadub.detectors.user_supplied
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
    path = unquote(parsed_url.path[len(container)+2:])

    container_client = blob_service_client.get_container_client(container)
    file_names = [
        blob.name
        for blob in container_client.list_blobs(path)
    ]

    file_content = {}
    for file_name in file_names:
        blob_client = blob_service_client.get_blob_client(blob=file_name, container=container)
        file_content[file_name] = blob_client.download_blob().readall()

    return file_content


def decode_text(documents: Dict[str, bytes], allowed_mime_types: Optional[List[str]] = None) -> Dict[str, str]:
    decoded_documents = {}  # type: Dict[str, str]
    if allowed_mime_types is None:
        allowed_mime_types = ['text/plain', 'application/octet-stream']
    logger = logging.getLogger('scrubadub.tests.benchmark_accuracy_real_data.decode_text')
    for name, value in documents.items():
        text = ""
        mime_type = magic.from_buffer(value, mime=True)
        if mime_type in ('application/x-empty'):
            logger.warning(f"The file '{name}' is empty, skipping.")
            continue
        if mime_type not in allowed_mime_types:
            logger.warning(f"The file '{name}' has mime type '{mime_type}', opening as plain text anyway.")
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
                # Remove \r from \r\n to leave \n. Assumes no newlines represented by simply '\r'.
                text = text.replace('\r', '')
                encoding = test_encoding
                break

        # If the decoded text is blank, but the encoded text isn't blank
        if len(text) == 0 and len(value) > 0:
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


def convert_to_bool(value: Any) -> bool:
    if isinstance(value, str):
        return value.strip().lower() in ('true', 'yes')
    return bool(value)


def load_known_pii(known_pii_locations: List[str],
                   storage_connection_string: Optional[str] = None) -> List[KnownFilthItem]:
    """This function loads tagged filth from a csv and transforms it into a dict that the detector can use"""
    start_time = time.time()
    click.echo("Loading Known Filth...")

    import pandas as pd
    # This will be a list of records containing all the info from the loaded tagged pii files
    known_pii = []  # type: List[Dict[str, Any]]

    logger = logging.getLogger('scrubadub.tests.benchmark_accuracy_real_data.load_known_pii')

    # These are the column names that we want
    target_cols = {'match', 'filth_type'}
    # These are some optional column names that we will use to filter extra columns out
    target_cols_optional = {'match_end', 'limit', 'ignore_case', 'ignore_whitespace', 'ignore_partial_word_matches'}
    # This is an alternate set of column names that are also accepted instead of the ones listed in `target_cols`
    target_cols_alt = {'pii_type', 'pii_start', 'pii_end'}

    # We loop over all tagged PII files
    for known_pii_location in known_pii_locations:
        file_data = load_files(known_pii_location, storage_connection_string=storage_connection_string)
        # Loop over the results from the load_files function, could be more than one file if we provide a directory
        # in `known_pii_location`
        for file_name, data in file_data.items():
            mime_type = magic.from_buffer(data, mime=True)
            pandas_reader = pd.read_csv
            if mime_type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
                pandas_reader = pd.read_excel
            else:
                data = decode_text({file_name: data}, allowed_mime_types=['application/csv'])[file_name].encode('utf-8')

            dataframe = None  # type: Optional[DataFrame]
            # Work out how many rows to skip in this loop, starting at zero going up to 9
            for n_rows_to_skip in range(10):
                dataframe = pandas_reader(io.BytesIO(data), skiprows=n_rows_to_skip, dtype={
                    'match': str,
                    'match_end': str,
                    'filth_type': str,
                    'pii_start': str,
                    'pii_end': str,
                    'pii_type': str,
                }).rename(columns=lambda x: x.strip())
                # If we find the `target_cols` then we found the correct number of rows to skip so we break from
                # this loop
                if (set(dataframe.columns.to_list()) & target_cols) == target_cols:
                    break
                # if we find the `target_cols_alt`, we convert those to the standard set of names and then break
                elif (set(dataframe.columns.to_list()) & target_cols_alt) == target_cols_alt:
                    dataframe = dataframe.rename(
                        columns={
                            'pii_type': 'filth_type',
                            'pii_start': 'match',
                            'pii_end': 'match_end',
                        }
                    )
                    dataframe = dataframe.replace({
                        "filth_type": {
                            "organisation": "organization",
                            "card-number": "credit_card",
                            "dob": "date_of_birth",
                            "driverslicence": "drivers_licence",
                            "postcode": "postalcode",
                            "licenceplate": "vehicle_licence_plate",
                        }
                    })
                    break
                dataframe = None

            # We weren't able to find the correct columns so raise an error
            if dataframe is None:
                raise ValueError(f'Unable to read file: {known_pii_location} Are the file format (csv or xslx) and '
                                 f'columns (match, match_end, filth_type and optionally limit) correct?')

            # strip() the main columns
            for col in ['match', 'match_end', 'filth_type']:
                dataframe[col] = dataframe[col].str.strip()

            # drop rows if the column 'match' has null values
            if pd.isnull(dataframe['match']).sum() > 0:
                dataframe = dataframe.dropna(axis='index', subset=['match'])

                logger.warning(
                    f"The KnownFilth column 'match' contains some null/blank entries in '{file_name}'. "
                    f"Skipping these rows."
                )
            # drop rows if the column 'filth_type' has null values
            if pd.isnull(dataframe['filth_type']).sum() > 0:
                dataframe = dataframe.dropna(axis='index', subset=['filth_type'])
                logger.warning(
                    f"The KnownFilth column 'filth_type' contains some null/blank entries in '{file_name}'. "
                    f"Skipping these rows."
                )
            # Convert the dataframe to a dict in records format and add it to the big list of tagged pii
            known_pii += dataframe[
                [col for col in dataframe.columns if col in (target_cols | target_cols_optional)]
            ].to_dict(orient='records')

    # Loop over each of the tagged pieces of pii
    for item in known_pii:
        for sub_item in ('limit', 'match_end', 'ignore_case', 'ignore_whitespace', 'ignore_partial_word_matches'):
            # if each of hte above keys exist, delete it if its empty
            if sub_item in item.keys():
                if pd.isnull(item[sub_item]):
                    del item[sub_item]
                elif isinstance(item[sub_item], str) and len(item[sub_item].strip()) == 0:
                    del item[sub_item]
                elif 'ignore' in sub_item:
                    # if ignore is in the name of the item, then try to convert it to a bool
                    item[sub_item] = convert_to_bool(item[sub_item])

            if 'ignore' in sub_item and sub_item not in item:
                # if ignore is not det then set it to true
                item[sub_item] = True

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


def scrub_documents(documents: Dict[str, str], known_filth_items: List[KnownFilthItem], locale: str,
                    detectors: Optional[str] = None) -> List[Filth]:
    start_time = time.time()
    click.echo("Initialising scrubadub...")

    detector_list = None  # type: Optional[List[str]]
    if detectors is not None:
        detector_list = [x.strip() for x in detectors.split(',')]

    scrubber = scrubadub.Scrubber(locale=locale, detector_list=detector_list)

    click.echo(f"Running with detectors: {', '.join(scrubber._detectors.keys())}")

    scrubber.add_detector(scrubadub.detectors.TaggedEvaluationFilthDetector(locale=locale, known_filth_items=known_filth_items))
    end_time = time.time()
    click.echo("Initialised scrubadub {:.2f}s".format(end_time-start_time))

    start_time = time.time()
    click.echo("Scrubbing {} documents".format(len(documents)))
    found_filth = list(scrubber.iter_filth_documents(documents))
    end_time = time.time()
    click.echo("Scrubbed documents in {:.2f}s".format(end_time-start_time))

    return found_filth


def load_complicated_detectors(user_supplied_pii: Optional[Sequence[str]] = None) -> Dict[str, bool]:
    detector_available = {
        'address': False,
        'address_sklearn': False,
        'date_of_birth': False,
        'spacy': False,
        'spacy_title': False,
        'stanford': False,
        'text_blob': False,
        'user_supplied': False,
    }

    try:
        import scrubadub.detectors.sklearn_address
        detector_name = scrubadub.detectors.sklearn_address.SklearnAddressDetector.name
        scrubadub.detectors.detector_configuration[detector_name]['autoload'] = True
        detector_available['address_sklearn'] = True
    except ImportError:
        pass
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
    try:
        import scrubadub.detectors.date_of_birth
        detector_available['date_of_birth'] = True
        detector_name = scrubadub.detectors.date_of_birth.DateOfBirthDetector.name
        scrubadub.detectors.detector_configuration[detector_name]['autoload'] = True
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
    # Disable spacy due to thinc.config.ConfigValidationError
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
    try:
        import scrubadub.detectors.spacy_name_title
        detector_available['spacy_title'] = True
    except ImportError:
        pass
    # Disable spacy due to thinc.config.ConfigValidationError
    if detector_available['spacy_title']:
        del scrubadub.detectors.detector_configuration[
            scrubadub.detectors.spacy_name_title.SpacyNameDetector.name
        ]

        # TODO: this only supports english models for spacy, this should be improved
        class SpacyTitleEnSmDetector(scrubadub.detectors.spacy_name_title.SpacyNameDetector):
            name = 'spacy_title_en_core_web_sm'
            def __init__(self, **kwargs):
                super(SpacyTitleEnSmDetector, self).__init__(model='en_core_web_sm', **kwargs)

        class SpacyTitleEnMdDetector(scrubadub.detectors.spacy_name_title.SpacyNameDetector):
            name = 'spacy_title_en_core_web_md'
            def __init__(self, **kwargs):
                super(SpacyTitleEnMdDetector, self).__init__(model='en_core_web_md', **kwargs)

        class SpacyTitleEnLgDetector(scrubadub.detectors.spacy_name_title.SpacyNameDetector):
            name = 'spacy_title_en_core_web_lg'
            def __init__(self, **kwargs):
                super(SpacyTitleEnLgDetector, self).__init__(model='en_core_web_lg', **kwargs)

        class SpacyTitleEnTrfDetector(scrubadub.detectors.spacy_name_title.SpacyNameDetector):
            name = 'spacy_title_en_core_web_trf'
            def __init__(self, **kwargs):
                super(SpacyTitleEnTrfDetector, self).__init__(model='en_core_web_trf', **kwargs)

        scrubadub.detectors.register_detector(SpacyTitleEnSmDetector, autoload=True)
        scrubadub.detectors.register_detector(SpacyTitleEnMdDetector, autoload=True)
        scrubadub.detectors.register_detector(SpacyTitleEnLgDetector, autoload=True)
        scrubadub.detectors.register_detector(SpacyTitleEnTrfDetector, autoload=True)

    if user_supplied_pii is not None:
        detector_available['user_supplied'] = True

        class LoadedUserSuppliedFilthDetector(scrubadub.detectors.user_supplied.UserSuppliedFilthDetector):
            name = scrubadub.detectors.user_supplied.UserSuppliedFilthDetector.name
            def __init__(self, **kwargs):
                known_filth_items = load_known_pii(user_supplied_pii)
                super(LoadedUserSuppliedFilthDetector, self).__init__(known_filth_items=known_filth_items, **kwargs)

        scrubadub.detectors.register_detector(LoadedUserSuppliedFilthDetector, autoload=True)

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
@click.option('--detectors', default=None, metavar='<locale>', type=click.STRING,
              help='Comma separated detectors to run')
@click.option('--groupby-documents', is_flag=True, help='Breakdown accuracies by document')
@click.option('--storage-connection-string', type=str, envvar='AZURE_STORAGE_CONNECTION_STRING', metavar='<string>',
              help='Connection string to azure bob storage (if needed)')
@click.option('--tagged-pii', '--known-pii', type=str, multiple=True, metavar='<file>',
              help="File containing tagged PII", callback=not_none_argument)
@click.option('--user-supplied-pii', type=str, multiple=True, metavar='<file>',
              help="File containing user-supplied PII")
@click.option('--filth-matching-dataset', type=click.File('wt'),
              help="Location of csv file to save detailed matching information to")
@click.option('--filth-matching-report', type=click.File('wt'),
              help="Location of markdown file to save matching report to")
@click.option('--debug-log', type=click.File('wt'),
              help="Location of a log file for log messages that may contain PII")
@click.argument('document', metavar='DOCUMENT', type=str, nargs=-1, callback=not_none_argument)
def main(document: Union[str, Sequence[str]], fast: bool, locale: str, storage_connection_string: Optional[str],
         tagged_pii: Sequence[str], user_supplied_pii: Sequence[str],
         filth_matching_dataset: Optional[click.utils.LazyFile], filth_matching_report: Optional[click.utils.LazyFile],
         debug_log: Optional[click.utils.LazyFile], detectors: Optional[str] = None, groupby_documents: bool = False):
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
        load_complicated_detectors(user_supplied_pii=user_supplied_pii)

    # Setup a logger that we can use to log things with possible PII data in that won't go to stdout
    logger = logging.getLogger('scrubadub')
    logger.handlers = []
    logger.setLevel(logging.NOTSET)

    if debug_log is not None:
        root_logger = logging.getLogger()
        for handler in root_logger.handlers:
            root_logger.removeHandler(handler)
        root_logger.setLevel(logging.WARNING)

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler = logging.FileHandler(debug_log.name, mode='wt')
        file_handler.setFormatter(formatter)

        root_logger.addHandler(file_handler)

    known_pii_locations = list(tagged_pii)
    known_filth_items = load_known_pii(
        known_pii_locations=known_pii_locations, storage_connection_string=storage_connection_string
    )

    documents_list = list(document)
    documents = load_documents(
        document_locations=documents_list, storage_connection_string=storage_connection_string
    )

    if len(documents) == 0:
        click.echo("ERROR: No documents were loaded.")
        return

    found_filth = scrub_documents(
        documents=documents, known_filth_items=known_filth_items, locale=locale, detectors=detectors
    )

    create_filth_summaries(found_filth, filth_matching_dataset, filth_matching_report)

    classification_report = get_filth_classification_report(found_filth)
    if classification_report is None:
        click.echo("ERROR: No Known Filth was found in the provided documents.")
        return

    click.echo("\n" + classification_report)

    if groupby_documents:
        classification_report = get_filth_classification_report(found_filth, groupby_documents=True)
        if classification_report is None:
            click.echo("ERROR: No Known Filth was found in the provided documents.")
            return

        click.echo("\n" + classification_report)

    classification_report = get_filth_classification_report(found_filth, combine_detectors=True)
    if classification_report is None:
        click.echo("ERROR: Combined classification report is None.")
        return

    click.echo("\n" + classification_report)


if __name__ == "__main__":
    main()
