import unittest

import scrubadub
import scrubadub.post_processors
from scrubadub.filth import MergedFilth, Filth


class ScrubberTestCase(unittest.TestCase):

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

    def test_filth_merge_placeholder(self):
        """filths should be merged into the biggest filth"""
        text = "you can skype me at john.doe"
        scrubber = scrubadub.Scrubber()
        for filth in scrubber.iter_filth(text):
            self.assertIsInstance(filth, MergedFilth)
            self.assertTrue('SKYPE' in filth.placeholder, filth.placeholder)
            self.assertTrue('EMAIL' in filth.placeholder, filth.placeholder)

    def test_add_detector_instance(self):
        """make sure adding an initialised detector works"""
        scrubber = scrubadub.Scrubber()
        scrubber.remove_detector('email')
        scrubber.add_detector(scrubadub.detectors.email.EmailDetector())

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

    def test_iter_not_return_filth(self):
        """make sure a detector cant return non filth"""
        class FakeFilth(Filth):
            name = 'fakerfilth'

        class BadDetector(scrubadub.detectors.Detector):
            filth_cls = FakeFilth
            def iter_filth(self, text):
                yield 'Non-filth'

        scrubber = scrubadub.Scrubber()
        scrubber._detectors = {'fakerfilth': BadDetector}
        with self.assertRaises(TypeError):
            list(scrubber.iter_filth('A fake document with no pii'))

    def test_dict_document(self):
        """check we can clean a dict of documents"""
        text = {
            'shark tales': 'the apple was eaten by a shark',
            'fish tales': 'the apple was not eaten by the fish',
        }
        scrubber = scrubadub.Scrubber()
        self.assertEqual(scrubber.clean(text), text)

        text_dirty = {
            'shark tales': 'shark sent example@example.com a complaint',
            'fish tales': 'the fish swam on by',
        }
        text_clean = {
            'shark tales': 'shark sent {{EMAIL}} a complaint',
            'fish tales': 'the fish swam on by',
        }
        scrubber = scrubadub.Scrubber()
        self.assertEqual(scrubber.clean(text_dirty), text_clean)

    def test_list_document(self):
        """check we can clean a list of documents"""
        text = [
            'the apple was eaten by a shark',
            'the apple was not eaten by the fish',
        ]
        scrubber = scrubadub.Scrubber()
        self.assertEqual(scrubber.clean(text), text)

        text_dirty = [
            'shark sent example@example.com a complaint',
            'the fish swam on by',
        ]
        text_clean = [
            'shark sent {{EMAIL}} a complaint',
            'the fish swam on by',
        ]
        scrubber = scrubadub.Scrubber()
        self.assertEqual(scrubber.clean(text_dirty), text_clean)

    def test_add_post_processor_instance(self):
        """make sure adding some post processors work"""
        scrubber = scrubadub.Scrubber()
        scrubber.add_post_processor(scrubadub.post_processors.HashReplacer(salt='example_salt', include_type=False))
        scrubber.add_post_processor(scrubadub.post_processors.PrefixSuffixReplacer(prefix='<<', suffix='>>'))
        print(scrubber._post_processors)
        text = scrubber.clean("hello from example@example.com")
        self.assertEqual(text, "hello from <<5A337A5C25F9D260>>")


    def test_add_post_processor_order(self):
        """make sure adding some post processors work"""
        scrubber = scrubadub.Scrubber()
        scrubber.add_post_processor(scrubadub.post_processors.FilthTypeReplacer(name='one'))
        scrubber.add_post_processor(scrubadub.post_processors.HashReplacer(name='two', salt='example_salt', include_type=False))
        scrubber.add_post_processor(scrubadub.post_processors.PrefixSuffixReplacer(name='three', prefix='<<', suffix='>>'))

        self.assertEqual([i for i, x in enumerate(scrubber._post_processors) if x.name == 'one'][0], 0)
        self.assertEqual([i for i, x in enumerate(scrubber._post_processors) if x.name == 'two'][0], 1)
        self.assertEqual([i for i, x in enumerate(scrubber._post_processors) if x.name == 'three'][0], 2)

        scrubber.add_post_processor(scrubadub.post_processors.FilthTypeReplacer(name='zero'), index=0)
        print(scrubber._post_processors)

        self.assertEqual([i for i, x in enumerate(scrubber._post_processors) if x.name == 'zero'][0], 0)
        self.assertEqual([i for i, x in enumerate(scrubber._post_processors) if x.name == 'one'][0], 1)
        self.assertEqual([i for i, x in enumerate(scrubber._post_processors) if x.name == 'two'][0], 2)
        self.assertEqual([i for i, x in enumerate(scrubber._post_processors) if x.name == 'three'][0], 3)
