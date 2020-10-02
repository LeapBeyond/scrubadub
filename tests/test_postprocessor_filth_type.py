import unittest

from scrubadub.post_processors.text_replacers.filth_type import FilthTypeReplacer
from scrubadub.filth import Filth, MergedFilth, EmailFilth


class FilthTypeReplacerTestCase(unittest.TestCase):
    def test_label_maker(self):
        """Test making labels from filths"""
        class TestFilth(Filth):
            type = 'test_type'

        self.assertEqual(
            FilthTypeReplacer.filth_label(TestFilth(0, 1, 'a')),
            'TEST_TYPE'
        )

        merged = MergedFilth(TestFilth(0, 2, 'ab'), EmailFilth(1, 2, 'b'))

        self.assertEqual(
            FilthTypeReplacer.filth_label(merged),
            'TEST_TYPE+EMAIL'
        )

        merged = MergedFilth(EmailFilth(0, 2, 'ab'), TestFilth(1, 2, 'b'))

        self.assertEqual(
            FilthTypeReplacer.filth_label(merged),
            'EMAIL+TEST_TYPE'
        )

        self.assertEqual(
            FilthTypeReplacer.filth_label(merged, separator='::'),
            'EMAIL::TEST_TYPE'
        )

        TestFilth.type = "other_test_type"

        self.assertEqual(
            FilthTypeReplacer.filth_label(TestFilth(0, 1, 'a')),
            'OTHER_TEST_TYPE'
        )

        self.assertEqual(
            FilthTypeReplacer.filth_label(EmailFilth(0, 1, 'a')),
            'EMAIL'
        )

        self.assertEqual(
            FilthTypeReplacer.filth_label(EmailFilth(0, 1, 'a'), upper=False),
            'email'
        )

    def test_process_filths(self):
        """Test that the process_filths behaves as expected"""
        class TestFilth(Filth):
            type = 'test_type'

        filths = [
            MergedFilth(EmailFilth(0, 2, 'ab'), TestFilth(1, 2, 'b')),
            EmailFilth(5, 6, 'c')
        ]

        post_processor = FilthTypeReplacer()
        filths = post_processor.process_filth(filths)

        self.assertEqual(filths[0].replacement_string, 'EMAIL+TEST_TYPE')
        self.assertEqual(filths[1].replacement_string, 'EMAIL')
