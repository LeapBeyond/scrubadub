import unittest

from scrubadub.post_processors.text_replacers.hash import HashReplacer
from scrubadub.filth import EmailFilth


class PrefixSuffixReplacerTestCase(unittest.TestCase):
    def test_usage(self):
        post_proc = HashReplacer()
        self.assertTrue(post_proc.salt is not None)
        self.assertIsInstance(post_proc.salt, bytes)
        self.assertGreater(len(post_proc.salt), 0)

        filths = [EmailFilth(0, 19, 'example@example.com')]
        self.assertEqual(filths[0].replacement_string, None)

        post_proc = HashReplacer(salt='example', include_type=True)
        filths = post_proc.process_filth(filths)
        self.assertEqual(filths[0].replacement_string, 'EMAIL-42FFCB267F8C5E6D')

        post_proc = HashReplacer(salt='example', include_type=False)
        filths = post_proc.process_filth(filths)
        self.assertEqual(filths[0].replacement_string, '42FFCB267F8C5E6D')

        post_proc = HashReplacer(salt='another_salt', include_type=False)
        filths = post_proc.process_filth(filths)
        self.assertEqual(filths[0].replacement_string, '87BB6F7ED5FE49C4')

        post_proc = HashReplacer(salt='another_salt', include_type=False, length=10)
        filths = post_proc.process_filth(filths)
        self.assertEqual(filths[0].replacement_string, '87BB6F7ED5')
        self.assertEqual(len(filths[0].replacement_string), 10)

        post_proc = HashReplacer(salt='another_salt', include_type=False, length=50)
        filths = post_proc.process_filth(filths)
        self.assertEqual(filths[0].replacement_string, '87BB6F7ED5FE49C4EA43D95A41F843D4FBB66D15C5AA41A7F7')
        self.assertEqual(len(filths[0].replacement_string), 50)
