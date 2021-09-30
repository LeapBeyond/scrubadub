import unittest
import catalogue
import scrubadub
import scrubadub.post_processors.catalogue


class PostProcessorConfigTestCase(unittest.TestCase):
    def test_register_post_processor(self):
        class NewPostProcessor(scrubadub.post_processors.PostProcessor):
            name = 'new_post_processor'

        scrubadub.post_processors.catalogue.register_post_processor(NewPostProcessor, False, -1)

        self.assertTrue(NewPostProcessor.name in scrubadub.post_processors.catalogue.post_processor_catalogue)
        self.assertFalse(NewPostProcessor.autoload)
        self.assertEqual(-1, NewPostProcessor.index)
        self.assertEqual(scrubadub.post_processors.catalogue.post_processor_catalogue.get(NewPostProcessor.name), NewPostProcessor)

        scrubadub.post_processors.catalogue.remove_post_processor(NewPostProcessor)
        with self.assertRaises(catalogue.RegistryError):
            scrubadub.post_processors.catalogue.post_processor_catalogue.get(NewPostProcessor.name)

        scrubadub.post_processors.catalogue.register_post_processor(NewPostProcessor, True, 7927)
        self.assertTrue(NewPostProcessor.name in scrubadub.post_processors.catalogue.post_processor_catalogue)
        self.assertTrue(NewPostProcessor.autoload)
        self.assertEqual(7927, NewPostProcessor.index)
        self.assertEqual(scrubadub.post_processors.catalogue.post_processor_catalogue.get(NewPostProcessor.name), NewPostProcessor)

        scrubadub.post_processors.catalogue.remove_post_processor(NewPostProcessor)
