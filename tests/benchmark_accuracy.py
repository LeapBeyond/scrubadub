import sys
import time

import scrubadub

from scrubadub.comparison import make_fake_document, get_filth_classification_report

run_spacy = False
run_stanford = False
run_address = False

run_slow = False

try:
    import scrubadub.detectors.spacy
    run_spacy = True
except ImportError:
    pass
try:
    import scrubadub.detectors.stanford_ner
    run_stanford = True
except ImportError:
    pass
try:
    import scrubadub.detectors.address
    run_address = True
except ImportError:
    pass


def main():
    general_docs = []
    known_general_pii = []
    address_docs = []
    known_address_pii = []
    # uk_phone_docs = []
    # known_uk_phone_pii = []
    start_time = time.time()
    for i_doc in range(50):
        filth_types = ['email', 'name', 'phone', 'postalcode', 'ssn', 'twitter', 'url']
        new_doc, new_known_pii = make_fake_document(paragraphs=2*len(filth_types), seed=i_doc, filth_types=filth_types)
        general_docs.append(new_doc)
        known_general_pii += new_known_pii

        #new_doc, new_known_pii = make_fake_document(paragraphs=4, seed=i_doc, filth_types=['name'])
        # Change the filth name to allow for comparison with NamedEntityDetector. Probably there is a better way to do it

        #for pii in new_known_pii:
       #     pii['filth_type'] = 'named_entity'

        #named_entity_docs.append(new_doc)
        #known_named_entity_pii += new_known_pii

        if run_address:
            new_doc, new_known_pii = make_fake_document(paragraphs=4, seed=i_doc, filth_types=['gb_address', 'us_address'])
            address_docs.append(new_doc)
            known_address_pii += new_known_pii

        # new_doc, new_known_pii = make_fake_document(
        #     faker=faker.Faker(locale='en_gb'), paragraphs=2, seed=i_doc, filth_types=['phone']
        # )
        # uk_phone_docs.append(new_doc)
        # known_uk_phone_pii += new_known_pii

    scrubber_time = time.time()
    scrubber = scrubadub.Scrubber()
    if run_spacy:
        scrubber.add_detector(scrubadub.detectors.spacy.SpacyEntityDetector(name='en_core_web_sm', model='en_core_web_sm'))
        if run_slow:
            scrubber.add_detector(scrubadub.detectors.spacy.SpacyEntityDetector(name='en_core_web_md', model='en_core_web_md'))
            scrubber.add_detector(scrubadub.detectors.spacy.SpacyEntityDetector(name='en_core_web_lg', model='en_core_web_lg'))
            scrubber.add_detector(scrubadub.detectors.spacy.SpacyEntityDetector(name='en_core_web_trf', model='en_core_web_trf'))
    if run_stanford and run_slow:
        scrubber.add_detector(scrubadub.detectors.stanford_ner.StanfordNERDetector())
    scrubber.add_detector(scrubadub.detectors.KnownFilthDetector(known_filth_items=known_general_pii))
    filth_list = list(scrubber.iter_filth_documents(general_docs))

    if run_address:
        scrubber = scrubadub.Scrubber(detector_list=[
            scrubadub.detectors.address.GBAddressDetector(),
            scrubadub.detectors.address.USAddressDetector(),
            scrubadub.detectors.KnownFilthDetector(known_filth_items=known_address_pii),
        ])
        filth_list += list(scrubber.iter_filth_documents(address_docs))

    # scrubber = scrubadub.Scrubber(detector_list=[
    #     scrubadub.detectors.PhoneDetector(region='gb', name='gb_phone'),
    #     scrubadub.detectors.KnownFilthDetector(known_filth_items=known_uk_phone_pii),
    # ])
    # filth_list += list(scrubber.iter_filth_documents(uk_phone_docs))

    end_time = time.time()
    print("Documents generated in {:.2f}s".format(scrubber_time-start_time))
    print("Scrubbed documents in  {:.2f}s".format(end_time-scrubber_time))
    print(get_filth_classification_report(filth_list))

    # scrubber_time = time.time()
    # scrubber = scrubadub.Scrubber(detector_list=[scrubadub.detectors.NamedEntityDetector(),
    #                                              scrubadub.detectors.KnownFilthDetector(known_filth_items=known_named_entity_pii)])
    # filth_list = list(scrubber.iter_filth_documents(named_entity_docs))
    # end_time = time.time()
    # print("Documents generated in {:.2f}s".format(scrubber_time-start_time))
    # print("Scrubbed documents in  {:.2f}s".format(end_time-scrubber_time))
    # print(get_filth_classification_report(filth_list))

    sys.exit(0)


if __name__ == "__main__":
    main()
