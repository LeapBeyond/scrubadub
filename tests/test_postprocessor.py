import unittest

import scrubadub
import scrubadub.post_processors
from scrubadub.filth import EmailFilth


class PostProcessorTestCase(unittest.TestCase):
    def test_post_processor_name(self):
        """make sure adding an initialised detector works"""
        filths = [
            EmailFilth(beg=0, end=5, text='e@e.c'),
            # EmailFilth(beg=5, end=10, text='e@e.c'),
        ]

        post_processor = scrubadub.post_processors.FilthReplacer(name='new_name')
        self.assertEqual(post_processor.name, 'new_name')
        new_filths = list(post_processor.process_filth(filths))
        self.assertEqual(len(new_filths), 1)
        self.assertEqual(new_filths[0].replacement_string, 'EMAIL')

    def test_post_processor_raise(self):
        """make sure adding an initialised detector works"""
        with self.assertRaises(NotImplementedError):
            scrubadub.post_processors.PostProcessor().process_filth([])
