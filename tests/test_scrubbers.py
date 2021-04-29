import copy
import warnings
import unittest

import scrubadub
import scrubadub.post_processors
from scrubadub.filth import MergedFilth, Filth


class ScrubberTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.maxDiff = None

    def test_clean_text(self):
        """make sure iter_filth doesn't fail with clean text"""
        text = 'the apple was eaten by a shark'
        scrubber = scrubadub.Scrubber()
        filths = [filth for filth in scrubber.iter_filth(text)]
        self.assertEqual(len(filths), 0)

    def test_filth_ordering(self):
        """make sure filth is returned in order"""
        scrubber = scrubadub.Scrubber()
        text = (
            "Alan can be reached by email alan@example.com or "
            "phone +1.312.456.6421"
        )
        order = []
        for filth in scrubber.iter_filth(text):
            order.append(filth.beg)
            order.append(filth.end)
        self.assertEqual(sorted(order), order)

    def test_filth_merge(self):
        """filth should merge properly"""
        # this looks like an email address 'me at john.doe' and skype
        text = "you can skype me at john.doe"
        scrubber = scrubadub.Scrubber()
        filths = [filth for filth in scrubber.iter_filth(text)]
        self.assertEqual(len(filths), 1)

    # def test_filth_merge_placeholder(self):
    #     """filths should be merged into the biggest filth"""
    #     text = "you can skype me at john.doe"
    #     scrubber = scrubadub.Scrubber()
    #     for filth in scrubber.iter_filth(text):
    #         self.assertIsInstance(filth, MergedFilth)
    #         # TODO:
    #         self.assertTrue('SKYPE' in filth.placeholder, filth.placeholder)
    #         self.assertTrue('EMAIL' in filth.placeholder, filth.placeholder)

    def test_add_detector_instance(self):
        """make sure adding an initialised detector works"""
        scrubber = scrubadub.Scrubber(detector_list=[])

        scrubber.add_detector(scrubadub.detectors.email.EmailDetector)
        self.assertEqual(len(scrubber._detectors), 1)
        self.assertEqual(list(scrubber._detectors.keys()), ['email'])

        scrubber.remove_detector('email')
        self.assertEqual(len(scrubber._detectors), 0)

        scrubber.add_detector('email')
        self.assertEqual(len(scrubber._detectors), 1)
        self.assertEqual(list(scrubber._detectors.keys()), ['email'])


    def test_add_duplicate_detector(self):
        """make sure adding a detector that already exists raises an error"""
        scrubber = scrubadub.Scrubber()
        with self.assertRaises(KeyError):
            scrubber.add_detector(scrubadub.detectors.email.EmailDetector)

    def test_add_detector_instance_with_name(self):
        """make sure adding a duplicate detector with a different name works"""
        scrubber = scrubadub.Scrubber(detector_list=[
            scrubadub.detectors.email.EmailDetector(name='email')
        ])
        scrubber.add_detector(scrubadub.detectors.email.EmailDetector(name='email_two'))
        scrubber.add_detector(scrubadub.detectors.email.EmailDetector(name='email_three'))

        self.assertEqual(len(scrubber._detectors), 3)
        self.assertEqual(sorted(list(scrubber._detectors.keys())), sorted(['email', 'email_two', 'email_three']))

        filth = list(scrubber.iter_filth('hello jane@example.com'))
        self.assertEqual(len(filth), 1)
        self.assertEqual(len(filth[0].filths), 3)
        self.assertEqual(
            sorted([f.detector_name for f in filth[0].filths]),
            sorted(['email', 'email_two', 'email_three'])
        )

    def test_add_non_detector(self):
        """make sure you can't add a detector that is not a Detector"""
        class NotDetector(object):
            pass

        scrubber = scrubadub.Scrubber()
        with self.assertRaises(TypeError):
            scrubber.add_detector(NotDetector)

        with self.assertRaises(ValueError):
            scrubber.add_detector('non_existant_detector')

    def test_remove_detector(self):
        """Test removing detectors"""
        import scrubadub.detectors.text_blob
        detector = scrubadub.detectors.EmailDetector(name='emailinator')
        scrubber = scrubadub.Scrubber(detector_list=[detector])
        scrubber.add_detector(scrubadub.detectors.EmailDetector)
        scrubber.add_detector('twitter')

        self.assertEqual(len(scrubber._detectors), 3)
        self.assertEqual(sorted(scrubber._detectors.keys()), sorted(['emailinator', 'email', 'twitter']))

        scrubber.remove_detector('twitter')
        self.assertEqual(len(scrubber._detectors), 2)
        self.assertEqual(sorted(scrubber._detectors.keys()), sorted(['emailinator', 'email']))

        scrubber.remove_detector(scrubadub.detectors.EmailDetector)
        self.assertEqual(len(scrubber._detectors), 1)
        self.assertEqual(sorted(scrubber._detectors.keys()), sorted(['emailinator']))

        scrubber.remove_detector(detector)
        self.assertEqual(len(scrubber._detectors), 0)

    def test_iter_not_return_filth(self):
        """make sure a detector cant return non filth"""
        class BadDetector(scrubadub.detectors.Detector):
            name = 'bad_detector'
            # TODO: investigate below
            def iter_filth(self, text, **kwargs):
                yield 'Non-filth'

        scrubber = scrubadub.Scrubber(detector_list=[BadDetector()])
        with self.assertRaises(TypeError) as err:
            list(scrubber.iter_filth('A fake document with no pii'))

    def test_dict_document(self):
        """check we can clean a dict of documents"""
        text = {
            'shark tales': 'the apple was eaten by a shark',
            'fish tales': 'the apple was not eaten by the fish',
        }
        scrubber = scrubadub.Scrubber()
        self.assertEqual(scrubber.clean_documents(text), text)

        text_dirty = {
            'shark tales': 'shark sent example@example.com a complaint',
            'fish tales': 'the fish swam on by',
        }
        text_clean = {
            'shark tales': 'shark sent {{EMAIL}} a complaint',
            'fish tales': 'the fish swam on by',
        }
        scrubber = scrubadub.Scrubber()
        self.assertEqual(scrubber.clean_documents(text_dirty), text_clean)

    def test_list_document(self):
        """check we can clean a list of documents"""
        text = [
            'the apple was eaten by a shark',
            'the apple was not eaten by the fish',
        ]
        scrubber = scrubadub.Scrubber()
        self.assertEqual(scrubber.clean_documents(text), text)

        text_dirty = [
            'shark sent example@example.com a complaint',
            'the fish swam on by',
        ]
        text_clean = [
            'shark sent {{EMAIL}} a complaint',
            'the fish swam on by',
        ]
        scrubber = scrubadub.Scrubber()
        self.assertEqual(scrubber.clean_documents(text_dirty), text_clean)

    def test_add_post_processor_instance(self):
        """make sure adding some post processors work"""
        scrubber = scrubadub.Scrubber()
        scrubber.add_post_processor(
            scrubadub.post_processors.FilthReplacer(hash_salt='example_salt', include_type=False, include_hash=True)
        )
        scrubber.add_post_processor(scrubadub.post_processors.PrefixSuffixReplacer(prefix='<<', suffix='>>'))
        text = scrubber.clean("hello from example@example.com")
        self.assertEqual("hello from <<5A337A5C25F9D260>>", text)


    def test_add_post_processor_order(self):
        """make sure adding some post processors work"""
        scrubber = scrubadub.Scrubber()
        scrubber.add_post_processor(scrubadub.post_processors.FilthReplacer(name='one'))
        scrubber.add_post_processor(scrubadub.post_processors.FilthReplacer(name='two', hash_salt='example_salt', include_type=False))
        scrubber.add_post_processor(scrubadub.post_processors.PrefixSuffixReplacer(name='three', prefix='<<', suffix='>>'))

        self.assertEqual([i for i, x in enumerate(scrubber._post_processors) if x.name == 'one'][0], 0)
        self.assertEqual([i for i, x in enumerate(scrubber._post_processors) if x.name == 'two'][0], 1)
        self.assertEqual([i for i, x in enumerate(scrubber._post_processors) if x.name == 'three'][0], 2)

        scrubber.add_post_processor(scrubadub.post_processors.FilthReplacer(name='zero'), index=0)

        self.assertEqual([i for i, x in enumerate(scrubber._post_processors) if x.name == 'zero'][0], 0)
        self.assertEqual([i for i, x in enumerate(scrubber._post_processors) if x.name == 'one'][0], 1)
        self.assertEqual([i for i, x in enumerate(scrubber._post_processors) if x.name == 'two'][0], 2)
        self.assertEqual([i for i, x in enumerate(scrubber._post_processors) if x.name == 'three'][0], 3)

    def test_add_duplicate_post_processor(self):
        """make sure adding a detector that already exists raises an error"""
        scrubber = scrubadub.Scrubber()
        scrubber.add_post_processor(scrubadub.post_processors.FilthReplacer)

        with self.assertRaises(KeyError):
            scrubber.add_post_processor(scrubadub.post_processors.FilthReplacer)

    def test_add_post_processor_instance_with_name(self):
        """make sure adding a duplicate post_processors with a different name works"""
        scrubber = scrubadub.Scrubber(post_processor_list=[
            scrubadub.post_processors.FilthReplacer(name='typeinator'),
            scrubadub.post_processors.PrefixSuffixReplacer(name='prefixor'),
        ])
        scrubber.add_post_processor(scrubadub.post_processors.PrefixSuffixReplacer(name='prefixor_two'))
        self.assertEqual(len(scrubber._post_processors), 3)
        filth = list(scrubber.iter_filth('hello jane@example.com'))
        self.assertEqual(len(filth), 1)
        self.assertEqual(filth[0].replacement_string, '{{{{EMAIL}}}}')

    def test_add_non_post_processor(self):
        """make sure you can't add a detector that is not a Detector"""

        class NotPostProcessor(object):
            pass

        scrubber = scrubadub.Scrubber()
        with self.assertRaises(TypeError):
            scrubber.add_post_processor(NotPostProcessor)

        with self.assertRaises(ValueError):
            scrubber.add_post_processor('not_really_the_name_of_a_detector')

    def test_remove_post_processor(self):
        """make sure you can't add a detector that is not a Detector"""
        post_processor = scrubadub.post_processors.FilthReplacer(name='typeinator')
        scrubber = scrubadub.Scrubber(post_processor_list=[post_processor])
        scrubber.add_post_processor(scrubadub.post_processors.PrefixSuffixReplacer)
        scrubber.add_post_processor('filth_replacer')

        self.assertEqual(len(scrubber._post_processors), 3)
        self.assertEqual([x.name for x in scrubber._post_processors], ['typeinator', 'prefix_suffix_replacer',
                                                                       'filth_replacer'])

        scrubber.remove_post_processor('filth_replacer')
        self.assertEqual(len(scrubber._post_processors), 2)
        self.assertEqual([x.name for x in scrubber._post_processors], ['typeinator', 'prefix_suffix_replacer'])

        scrubber.remove_post_processor(scrubadub.post_processors.PrefixSuffixReplacer)
        self.assertEqual(len(scrubber._post_processors), 1)
        self.assertEqual([x.name for x in scrubber._post_processors], ['typeinator'])

        scrubber.remove_post_processor(post_processor)
        self.assertEqual(len(scrubber._post_processors), 0)
        self.assertEqual([x.name for x in scrubber._post_processors], [])


    def test_sorting(self):
        """Ensure that filths are sorted correctly"""
        filths = scrubadub.Scrubber._sort_filths([
            Filth(beg=6, end=7),
            Filth(beg=2, end=3),
            Filth(beg=0, end=1),
            Filth(beg=4, end=5),
        ])
        self.assertEqual(
            [(f.beg, f.end) for f in filths],
            [(0, 1), (2, 3), (4, 5), (6, 7)]
        )

        filths = scrubadub.Scrubber._sort_filths([
            Filth(beg=7, end=8),
            Filth(beg=0, end=1),
            Filth(beg=4, end=5),
            Filth(beg=0, end=3),
            Filth(beg=5, end=8),
        ])
        self.assertEqual(
            [(f.beg, f.end) for f in filths],
            [(0, 3), (0, 1), (4, 5), (5, 8), (7, 8)]
        )

        filths = scrubadub.Scrubber._sort_filths([
            Filth(beg=5, end=8, document_name='a'),
            Filth(beg=0, end=3, document_name='b'),
            Filth(beg=4, end=5, document_name='b'),
            Filth(beg=7, end=8, document_name='a'),
            Filth(beg=0, end=1, document_name='a'),
        ])
        self.assertEqual(
            [(f.document_name, f.beg, f.end) for f in filths],
            [('a', 0, 1), ('a', 5, 8), ('a', 7, 8), ('b', 0, 3), ('b', 4, 5)]
        )

    def test_merging(self):
        """Ensure that filths are merged correctly"""
        filths = scrubadub.Scrubber._merge_filths([
            Filth(beg=6, end=7, text='a'),
            Filth(beg=2, end=3, text='a'),
            Filth(beg=0, end=1, text='a'),
            Filth(beg=4, end=5, text='a'),
        ])
        self.assertEqual(
            [(f.beg, f.end) for f in filths],
            [(0, 1), (2, 3), (4, 5), (6, 7)]
        )

        filths = scrubadub.Scrubber._merge_filths([
            Filth(beg=7, end=8, text='a'),
            Filth(beg=0, end=1, text='a'),
            Filth(beg=4, end=5, text='a'),
            Filth(beg=0, end=3, text='aaa'),
            Filth(beg=5, end=8, text='aaa'),
        ])
        self.assertEqual(
            [(f.beg, f.end) for f in filths],
            [(0, 3), (4, 8)]
        )

        filths = scrubadub.Scrubber._merge_filths([
            Filth(beg=5, end=8, text='aaa', document_name='a'),
            Filth(beg=0, end=3, text='aaa', document_name='b'),
            Filth(beg=4, end=5, text='a', document_name='b'),
            Filth(beg=7, end=8, text='a', document_name='a'),
            Filth(beg=0, end=1, text='a', document_name='a'),
        ])
        self.assertEqual(
            [(f.document_name, f.beg, f.end) for f in filths],
            [('a', 0, 1), ('a', 5, 8), ('b', 0, 3), ('b', 4, 5)]
        )

        filths = scrubadub.Scrubber._merge_filths([
            Filth(beg=5, end=8, text='aaa', document_name=None),
            Filth(beg=0, end=3, text='aaa', document_name='b'),
            Filth(beg=4, end=5, text='a', document_name='b'),
            Filth(beg=7, end=8, text='a', document_name=None),
            Filth(beg=0, end=1, text='a', document_name='a'),
        ])
        self.assertEqual(
            [(f.document_name, f.beg, f.end) for f in filths],
            [(None, 5, 8), ('a', 0, 1), ('b', 0, 3), ('b', 4, 5)]
        )

    def test_list_filth_documents_dict(self):
        """Test the iter_filth_documents funtion with a dict"""
        scrubber = scrubadub.Scrubber(post_processor_list=[scrubadub.post_processors.FilthReplacer()])
        docs = {
            "first.txt": "This is a test message for example@example.com",
            "second.txt": "Hello @Jane call me on +33 4 41 26 62 36.",
        }
        filth_list_one = list(scrubber.iter_filth_documents(docs, run_post_processors=True))
        filth_list_two = list(scrubber.iter_filth_documents(docs, run_post_processors=False))
        for filths in [filth_list_one, filth_list_two]:
            self.assertEqual(
                scrubadub.Scrubber._sort_filths([
                    scrubadub.filth.EmailFilth(
                        text='example@example.com', document_name='first.txt', detector_name='email', beg=27, end=46,
                        locale='en_US'
                    ),
                    scrubadub.filth.TwitterFilth(
                        text='@Jane', document_name='second.txt', detector_name='twitter', beg=6, end=11, locale='en_US'
                    ),
                    scrubadub.filth.PhoneFilth(
                        text='+33 4 41 26 62 36', document_name='second.txt', detector_name='phone', beg=23, end=40,
                        locale='en_US'
                    ),
                ]),
                scrubadub.Scrubber._sort_filths(filths),
            )

    def test_list_filth_documents_list(self):
        """Test the iter_filth_documents function with a list"""
        scrubber = scrubadub.Scrubber(post_processor_list=[scrubadub.post_processors.FilthReplacer()])
        docs = [
            "This is a test message for example@example.com",
            "Hello @Jane call me on +33 4 41 26 62 36.",
        ]
        filth_list_one = list(scrubber.iter_filth_documents(docs, run_post_processors=True))
        filth_list_two = list(scrubber.iter_filth_documents(docs, run_post_processors=False))
        for filths in [filth_list_one, filth_list_two]:
            self.assertEqual(
                [
                    scrubadub.filth.EmailFilth(
                        text='example@example.com', document_name='0', detector_name='email', beg=27, end=46,
                        locale='en_US'
                    ),
                    scrubadub.filth.TwitterFilth(
                        text='@Jane', document_name='1', detector_name='twitter', beg=6, end=11, locale='en_US'
                    ),
                    scrubadub.filth.PhoneFilth(
                        text='+33 4 41 26 62 36', document_name='1', detector_name='phone', beg=23, end=40,
                        locale='en_US'
                    ),
                ],
                filths,
            )

    def test_clean_documents_wrong_type(self):
        """Test that an error is thrown if document arguments are not a list of strings or a dict"""
        doc_list_of_numbers = [0, 1, 2, '3']
        doc_string = 'String'

        scrubber = scrubadub.Scrubber()

        with self.assertRaises(TypeError):
            scrubber.clean_documents(documents=doc_list_of_numbers)

        with self.assertRaises(TypeError):
            scrubber.clean_documents(documents=doc_string)

        with self.assertRaises(TypeError):
            list(scrubber.iter_filth_documents(documents=doc_list_of_numbers))

        with self.assertRaises(TypeError):
            list(scrubber.iter_filth_documents(documents=doc_string))

    def test_detector_with_non_supported_local_not_added(self):
        """Test to see if a detector with a non-supported locale can be added to a scrubber"""

        class FRLocaleDetector(scrubadub.detectors.Detector):
            name = 'fr_locale'
            @classmethod
            def supported_locale(cls, locale: str) -> bool:
                language, region = cls.locale_split(locale)
                return region == 'FR'

        orig_config = copy.copy(scrubadub.detectors.detector_configuration)
        try:
            scrubadub.detectors.detector_configuration = {}
            scrubadub.detectors.register_detector(FRLocaleDetector, autoload=True)

            scrubber = scrubadub.Scrubber(locale='en_GB')
            self.assertEqual(len(scrubber._detectors), 0)

            with warnings.catch_warnings(record=True) as warning_context:
                warnings.simplefilter("always")
                try:
                    scrubber = scrubadub.Scrubber(detector_list=[FRLocaleDetector(locale='fr_FR')], locale='en_US')
                finally:
                    warnings.simplefilter("default")
                self.assertEqual(sum([issubclass(w.category, UserWarning) for w in warning_context]), 1)

            self.assertEqual(len(scrubber._detectors), 1)

            scrubber = scrubadub.Scrubber(locale='fr_FR')
            self.assertEqual(len(scrubber._detectors), 1)
        finally:
            scrubadub.detectors.detector_configuration = orig_config
