import unittest

import scrubadub.filth
from scrubadub.post_processors.filth_replacer import FilthReplacer
from scrubadub.filth import Filth, MergedFilth, EmailFilth


class FilthTypeReplacerTestCase(unittest.TestCase):
    def test_label_maker(self):
        """Test making labels from filths"""
        class TestFilth(Filth):
            type = 'test_type'

        filth_replacer = FilthReplacer()
        self.assertEqual(
            filth_replacer.filth_label(TestFilth(0, 1, 'a')),
            'TEST_TYPE'
        )

        merged = MergedFilth(TestFilth(0, 2, 'ab'), EmailFilth(1, 2, 'b'))

        self.assertEqual(
            filth_replacer.filth_label(merged),
            'EMAIL+TEST_TYPE'
        )

        merged = MergedFilth(EmailFilth(0, 2, 'ab'), TestFilth(1, 2, 'b'))

        self.assertEqual(
            filth_replacer.filth_label(merged),
            'EMAIL+TEST_TYPE'
        )

        filth_replacer = FilthReplacer(separator='::')
        self.assertEqual(
            filth_replacer.filth_label(merged),
            'EMAIL::TEST_TYPE'
        )

        filth_replacer = FilthReplacer()
        TestFilth.type = "other_test_type"

        self.assertEqual(
            filth_replacer.filth_label(TestFilth(0, 1, 'a')),
            'OTHER_TEST_TYPE'
        )

        self.assertEqual(
            filth_replacer.filth_label(EmailFilth(0, 1, 'a')),
            'EMAIL'
        )

        filth_replacer = FilthReplacer(include_count=True)
        filth_replacer.reset_lookup()
        self.assertEqual(filth_replacer.filth_label(EmailFilth(0, 1, 'a')), 'EMAIL-0')
        self.assertEqual(filth_replacer.filth_label(EmailFilth(0, 1, 'b')), 'EMAIL-1')
        self.assertEqual(filth_replacer.filth_label(EmailFilth(0, 1, 'a')), 'EMAIL-0')
        self.assertEqual(filth_replacer.filth_label(EmailFilth(0, 1, 'c')), 'EMAIL-2')

        filth_replacer = FilthReplacer(uppercase=False)
        self.assertEqual(filth_replacer.filth_label(EmailFilth(0, 1, 'a')), 'email')

    def test_process_filths(self):
        """Test that the process_filths behaves as expected"""
        class TestFilth(Filth):
            type = 'test_type'

        filths = [
            MergedFilth(EmailFilth(0, 2, 'ab'), TestFilth(1, 2, 'b')),
            EmailFilth(5, 6, 'c')
        ]

        post_processor = FilthReplacer()
        filths = post_processor.process_filth(filths)

        self.assertEqual(filths[0].replacement_string, 'EMAIL+TEST_TYPE')
        self.assertEqual(filths[1].replacement_string, 'EMAIL')

    def test_hashing(self):
        post_proc = FilthReplacer()
        self.assertTrue(post_proc.hash_salt is not None)
        self.assertIsInstance(post_proc.hash_salt, bytes)
        self.assertGreater(len(post_proc.hash_salt), 0)

        filths = [EmailFilth(0, 19, 'example@example.com')]
        self.assertEqual(filths[0].replacement_string, None)

        post_proc = FilthReplacer(hash_salt='example', include_type=True, include_hash=True)
        filths = post_proc.process_filth(filths)
        self.assertEqual(filths[0].replacement_string, 'EMAIL-42FFCB267F8C5E6D')

        post_proc = FilthReplacer(hash_salt='example', include_type=True, include_count=True, include_hash=True)
        post_proc.reset_lookup()
        filths = post_proc.process_filth(filths)
        self.assertEqual(filths[0].replacement_string, 'EMAIL-0-42FFCB267F8C5E6D')

        post_proc = FilthReplacer(hash_salt='example', include_type=False, include_hash=True)
        filths = post_proc.process_filth(filths)
        self.assertEqual(filths[0].replacement_string, '42FFCB267F8C5E6D')

        post_proc = FilthReplacer(hash_salt='another_salt', include_type=False, include_hash=True)
        filths = post_proc.process_filth(filths)
        self.assertEqual(filths[0].replacement_string, '87BB6F7ED5FE49C4')

        post_proc = FilthReplacer(hash_salt='another_salt', include_type=False, hash_length=10, include_hash=True)
        filths = post_proc.process_filth(filths)
        self.assertEqual(filths[0].replacement_string, '87BB6F7ED5')
        self.assertEqual(len(filths[0].replacement_string), 10)

        post_proc = FilthReplacer(hash_salt='another_salt', include_type=False, hash_length=50, include_hash=True)
        filths = post_proc.process_filth(filths)
        self.assertEqual(filths[0].replacement_string, '87BB6F7ED5FE49C4EA43D95A41F843D4FBB66D15C5AA41A7F7')
        self.assertEqual(len(filths[0].replacement_string), 50)

    def test_bad_filth(self):
        """Test making labels from a filth without a type"""
        class TestFilth(Filth):
            type = None

        filth_replacer = FilthReplacer()
        self.assertEqual(
            filth_replacer.filth_label(TestFilth(0, 1, 'a')),
            ''
        )

    def test_tagged_filth(self):
        """Test making labels from a tagged filth"""
        filth_replacer = FilthReplacer()
        self.assertEqual(
            filth_replacer.filth_label(scrubadub.filth.TaggedEvaluationFilth(0, 1, 'a', comparison_type='phone')),
            'TAGGED_PHONE'
        )

    def test_all_disabled(self):
        """Test making labels when everything is disabled"""
        filth_replacer = FilthReplacer(include_type=False, include_hash=False, include_count=False)
        self.assertEqual(
            filth_replacer.filth_label(scrubadub.filth.TaggedEvaluationFilth(0, 1, 'a', comparison_type='phone')),
            'FILTH'
        )