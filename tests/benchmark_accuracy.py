#!/usr/bin/env python3

import time
import copy
import click
import random

import scrubadub.detectors.catalogue
from faker import Faker
from typing import List, Union, Dict, Optional, Tuple

import scrubadub
from scrubadub.detectors.base import Detector
from scrubadub.filth import Filth
from scrubadub.comparison import make_fake_document, get_filth_classification_report


FILTH_IN_LOCALES = {
    'en_US': ['address', 'email', 'name', 'phone', 'social_security_number', 'twitter', 'url'],
    'en_GB': ['address', 'phone', 'postalcode'],
}


def generate_and_scrub(locale: str, filth_list: List[str], detectors: List[Union[str, Detector]], n_docs: int = 50) -> List[Filth]:
    documents = []
    known_pii = []

    click.echo("Generating {} docs with filth: {}".format(locale, ", ".join(filth_list)))
    start_time = time.time()

    for i_doc in range(n_docs):
        new_doc, new_known_pii = make_fake_document(paragraphs=2*len(filth_list), locale=locale, seed=None,
                                                    filth_types=filth_list)
        documents.append(new_doc)
        known_pii += new_known_pii

    scrubber_time = time.time()
    click.echo("Scrubbing with detectors: {}".format(', '.join(detectors)))

    detectors.append(scrubadub.detectors.TaggedEvaluationFilthDetector(locale=locale, known_filth_items=known_pii))
    scrubber = scrubadub.Scrubber(locale=locale, detector_list=detectors)
    found_filth = list(scrubber.iter_filth_documents(documents))

    end_time = time.time()
    click.echo("Documents generated in {:.2f}s".format(scrubber_time-start_time))
    click.echo("Scrubbed documents in  {:.2f}s".format(end_time-scrubber_time))

    return found_filth


def document_accuracy_settings(locales: List[str], detector_available: Dict[str, bool], run_slow: bool = False,
                               limit_detectors: Optional[str] = False) -> List[Tuple[str, List[str], str]]:
    """This works out what should be executed"""
    global FILTH_IN_LOCALES
    run_settings = []  # type: List[Tuple[str, List[str], str]]

    detector_list = None  # type: Optional[List[str]]
    if limit_detectors is not None:
        if isinstance(limit_detectors, str):
            detector_list = [x.strip() for x in limit_detectors.split(',')]

    for locale in locales:
        detectors = []
        filth_list = copy.copy(FILTH_IN_LOCALES[locale])

        for filth in filth_list:
            if filth == 'address':
                filth_list = [x for x in filth_list if x != 'address']
                add_dets = []
                if detector_available['sklearn_address'] and locale == 'en_GB' \
                        and (detector_list is None or 'sklearn_address' in detector_list):
                    add_dets.append('sklearn_address')
                if detector_available['address'] and run_slow \
                        and (detector_list is None or 'address' in detector_list):
                    add_dets.append('address')
                if len(add_dets) > 0:
                    run_settings += [
                        (locale, ['address'], add_dets)
                    ]
            elif filth == 'name':
                added_name_detector = False
                if detector_available['spacy']:
                    if detector_list is None or 'spacy' in detector_list:
                        detectors.append('spacy_en_core_web_sm')
                        added_name_detector = True
                        if run_slow:
                            detectors += ['spacy_en_core_web_md', 'spacy_en_core_web_lg', 'spacy_en_core_web_trf']
                    else:
                        for x in ['spacy_en_core_web_sm', 'spacy_en_core_web_md', 'spacy_en_core_web_lg',
                                  'spacy_en_core_web_trf']:
                            if x in detector_list:
                                detectors.append(x)
                                added_name_detector = True
                if detector_available['spacy_name']:
                    if detector_list is None or 'spacy_name' in detector_list:
                        detectors.append('spacy_name_en_core_web_sm')
                        added_name_detector = True
                        if run_slow:
                            detectors += [
                                'spacy_name_en_core_web_md', 'spacy_name_en_core_web_lg',
                                'spacy_name_en_core_web_trf'
                            ]
                    else:
                        for x in ['spacy_name_en_core_web_sm', 'spacy_name_en_core_web_md',
                                  'spacy_name_en_core_web_lg', 'spacy_name_en_core_web_trf']:
                            if x in detector_list:
                                detectors.append(x)
                                added_name_detector = True
                if run_slow:
                    if detector_available['text_blob'] \
                            and (detector_list is None or 'text_blob' in detector_list):
                        detectors.append('text_blob_name')
                        added_name_detector = True
                    if detector_available['stanford'] \
                            and (detector_list is None or 'stanford' in detector_list):
                        detectors.append('stanford')
                        added_name_detector = True
                if not added_name_detector:
                    filth_list = [x for x in filth_list if x != 'name']
            else:
                if detector_list is None or filth in detector_list:
                    detectors.append(filth)

        if len(filth_list) > 0 and len(detectors) > 0:
            run_settings += [(locale, filth_list, detectors)]

    return run_settings


def load_complicated_detectors(run_slow: bool) -> Dict[str, bool]:
    detector_available = {
        'address': False,
        'sklearn_address': False,
        'date_of_birth': False,
        'spacy': False,
        'spacy_name': False,
        'stanford': False,
        'text_blob': False,
        'user_supplied': False,
    }
    try:
        import scrubadub_address_sklearn
        detector_available['sklearn_address'] = True
    except ImportError:
        pass
    if not detector_available['sklearn_address']:
        try:
            import scrubadub.detectors.sklearn_address
            detector_available['sklearn_address'] = True
        except ImportError:
            pass
    try:
        import scrubadub.detectors.text_blob
        detector_available['text_blob'] = True
    except ImportError:
        pass
    try:
        import scrubadub.detectors.date_of_birth
        scrubadub.detectors.date_of_birth.DateOfBirthDetector.autoload = True
        detector_available['date_of_birth'] = True
        # scrubadub.detectors.register_detector(scrubadub.detectors.date_of_birth.DateOfBirthDetector, autoload=True)
    except ImportError:
        pass

    if run_slow:
        try:
            import scrubadub_stanford
            detector_available['stanford'] = True
        except ImportError:
            pass
        if not detector_available['stanford']:
            try:
                import scrubadub.detectors.stanford
                detector_available['stanford'] = True
            except ImportError:
                pass
        try:
            import scrubadub_address
            detector_available['address'] = True
        except ImportError:
            pass
        if not detector_available['address']:
            try:
                import scrubadub.detectors.address
                detector_available['address'] = True
            except ImportError:
                pass
        try:
            import scrubadub_spacy
            detector_available['spacy'] = True
        except ImportError:
            pass
        if not detector_available['spacy']:
            try:
                import scrubadub.detectors.spacy
                detector_available['spacy'] = True
            except ImportError:
                pass
        # Disable spacy due to thinc.config.ConfigValidationError
        if detector_available['spacy']:
            SpacyEntityDetector = scrubadub.detectors.detector_catalogue.get('spacy')

            # TODO: this only supports english models for spacy, this should be improved
            class SpacyEnSmDetector(SpacyEntityDetector):
                name = 'spacy_en_core_web_sm'
                def __init__(self, **kwargs):
                    super(SpacyEnSmDetector, self).__init__(model='en_core_web_sm', **kwargs)

            class SpacyEnMdDetector(SpacyEntityDetector):
                name = 'spacy_en_core_web_md'
                def __init__(self, **kwargs):
                    super(SpacyEnMdDetector, self).__init__(model='en_core_web_md', **kwargs)

            class SpacyEnLgDetector(SpacyEntityDetector):
                name = 'spacy_en_core_web_lg'
                def __init__(self, **kwargs):
                    super(SpacyEnLgDetector, self).__init__(model='en_core_web_lg', **kwargs)

            class SpacyEnTrfDetector(SpacyEntityDetector):
                name = 'spacy_en_core_web_trf'
                def __init__(self, **kwargs):
                    super(SpacyEnTrfDetector, self).__init__(model='en_core_web_trf', **kwargs)

            scrubadub.detectors.catalogue.register_detector(SpacyEnSmDetector, autoload=True)
            scrubadub.detectors.catalogue.register_detector(SpacyEnMdDetector, autoload=True)
            scrubadub.detectors.catalogue.register_detector(SpacyEnLgDetector, autoload=True)
            scrubadub.detectors.catalogue.register_detector(SpacyEnTrfDetector, autoload=True)
            scrubadub.detectors.remove_detector('spacy')
        try:
            import scrubadub.detectors.spacy_name_title
            detector_available['spacy_name'] = True
        except ImportError:
            pass
        # Disable spacy due to thinc.config.ConfigValidationError
        if detector_available['spacy_name']:
            SpacyNameDetector = scrubadub.detectors.detector_catalogue.get('spacy_name')

            # TODO: this only supports english models for spacy, this should be improved
            class SpacyTitleEnSmDetector(SpacyNameDetector):
                name = 'spacy_name_en_core_web_sm'
                def __init__(self, **kwargs):
                    super(SpacyTitleEnSmDetector, self).__init__(model='en_core_web_sm', **kwargs)

            class SpacyTitleEnMdDetector(SpacyNameDetector):
                name = 'spacy_name_en_core_web_md'
                def __init__(self, **kwargs):
                    super(SpacyTitleEnMdDetector, self).__init__(model='en_core_web_md', **kwargs)

            class SpacyTitleEnLgDetector(SpacyNameDetector):
                name = 'spacy_name_en_core_web_lg'
                def __init__(self, **kwargs):
                    super(SpacyTitleEnLgDetector, self).__init__(model='en_core_web_lg', **kwargs)

            class SpacyTitleEnTrfDetector(SpacyNameDetector):
                name = 'spacy_name_en_core_web_trf'
                def __init__(self, **kwargs):
                    super(SpacyTitleEnTrfDetector, self).__init__(model='en_core_web_trf', **kwargs)

            scrubadub.detectors.catalogue.register_detector(SpacyTitleEnSmDetector, autoload=True)
            scrubadub.detectors.catalogue.register_detector(SpacyTitleEnMdDetector, autoload=True)
            scrubadub.detectors.catalogue.register_detector(SpacyTitleEnLgDetector, autoload=True)
            scrubadub.detectors.catalogue.register_detector(SpacyTitleEnTrfDetector, autoload=True)
            scrubadub.detectors.remove_detector('spacy_name')

    return detector_available


@click.command()
@click.option('--ndocs', help='Number of fake documents', default=50, type=click.INT, show_default=True)
@click.option('--seed', help='Document generation seed', default=1234, type=click.INT, show_default=True)
@click.option('--fast', is_flag=True, help='Only run fast detectors')
@click.option('--combine-detectors', is_flag=True, help='Print statistics for combined detectors')
@click.option('--groupby-documents', is_flag=True, help='Breakdown accuracies by document')
@click.option('--locales', default=','.join(FILTH_IN_LOCALES.keys()), show_default=True,
               metavar='<locale>', type=click.STRING, help='Locales to run with')
@click.option('--detectors', default=None, metavar='<locale>', type=click.STRING,
              help='Comma separated detectors to run')
def main(fast: bool, combine_detectors: bool, locales: Union[str, List[str]], ndocs: int = 50, seed: int = 1234,
         detectors: Optional[str] = None, groupby_documents: bool = False):
    """Test scrubadub accuracy using fake data."""
    run_slow = not fast

    if isinstance(locales, str):
        locales_list = [x.strip() for x in locales.split(',')]
    else:
        locales_list = list(locales)

    detector_available = load_complicated_detectors(run_slow)

    settings = document_accuracy_settings(
        locales=locales_list, run_slow=run_slow, detector_available=detector_available, limit_detectors=detectors,
    )

    Faker.seed(seed)
    random.seed(seed)

    found_filth = []
    for locale, filth_list, detectors in settings:
        found_filth += generate_and_scrub(locale, filth_list, detectors, n_docs=ndocs)

    if groupby_documents:
        classification_report = get_filth_classification_report(found_filth, groupby_documents=True)
        if classification_report is None:
            click.echo("ERROR: No Known Filth was found in the provided documents.")
            return

        click.echo("\n" + classification_report)

    print(get_filth_classification_report(found_filth, combine_detectors=False))
    if combine_detectors:
        print(get_filth_classification_report(found_filth, combine_detectors=True))

    # TODO: check seed sets things correctly


if __name__ == "__main__":
    main()
