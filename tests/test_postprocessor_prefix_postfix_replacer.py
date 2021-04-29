import unittest

from scrubadub.post_processors.prefix_suffix import PrefixSuffixReplacer
from scrubadub.filth import EmailFilth


class PrefixSuffixReplacerTestCase(unittest.TestCase):
    def test_usage(self):
        post_proc = PrefixSuffixReplacer()
        filths = [EmailFilth(0, 19, 'example@example.com')]
        self.assertEqual(filths[0].replacement_string, None)

        filths = post_proc.process_filth(filths)
        self.assertEqual(filths[0].replacement_string, '{{EMAIL}}')

        post_proc = PrefixSuffixReplacer(prefix=None, suffix='>>')
        filths = post_proc.process_filth(filths)
        self.assertEqual(filths[0].replacement_string, '{{EMAIL}}>>')

        post_proc = PrefixSuffixReplacer(prefix='<<', suffix=None)
        filths = post_proc.process_filth(filths)
        self.assertEqual(filths[0].replacement_string, '<<{{EMAIL}}>>')

        post_proc = PrefixSuffixReplacer(prefix='||', suffix='||')
        filths = post_proc.process_filth(filths)
        self.assertEqual(filths[0].replacement_string, '||<<{{EMAIL}}>>||')