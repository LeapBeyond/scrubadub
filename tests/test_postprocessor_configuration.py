import unittest
import scrubadub


class PostProcessorConfigTestCase(unittest.TestCase):
    def test_register_detector(self):
        class NewPostProcessor(scrubadub.post_processors.PostProcessor):
            name = 'new_post_processor'

        scrubadub.post_processors.register_post_processor(NewPostProcessor, False, -1)
        self.assertTrue(NewPostProcessor.name in scrubadub.post_processors.post_processor_configuration)
        self.assertEqual(scrubadub.post_processors.post_processor_configuration[NewPostProcessor.name]['autoload'], False)
        self.assertEqual(scrubadub.post_processors.post_processor_configuration[NewPostProcessor.name]['index'], -1)
        self.assertEqual(scrubadub.post_processors.post_processor_configuration[NewPostProcessor.name]['post_processor'], NewPostProcessor)

        scrubadub.post_processors.post_processor_configuration.pop(NewPostProcessor.name)
        self.assertTrue(NewPostProcessor.name not in scrubadub.post_processors.post_processor_configuration)

        scrubadub.post_processors.register_post_processor(NewPostProcessor, True, 0)
        self.assertTrue(NewPostProcessor.name in scrubadub.post_processors.post_processor_configuration)
        self.assertEqual(scrubadub.post_processors.post_processor_configuration[NewPostProcessor.name]['autoload'], True)
        self.assertEqual(scrubadub.post_processors.post_processor_configuration[NewPostProcessor.name]['index'], 0)
        self.assertEqual(scrubadub.post_processors.post_processor_configuration[NewPostProcessor.name]['post_processor'], NewPostProcessor)

        scrubadub.post_processors.post_processor_configuration.pop(NewPostProcessor.name)
