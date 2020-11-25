import unittest
import scrubadub


class APITestCase(unittest.TestCase):

    def test_clean(self):
        """Test the top level clean api"""
        self.assertEqual(
            "This is a test message for {{EMAIL}}",
            scrubadub.clean("This is a test message for example@exampe.com"),
        )

    def test_clean_documents(self):
        """Test the top level clean_documents api"""
        self.assertEqual(
            {
                "first.txt": "This is a test message for {{EMAIL}}",
                "second.txt": "Hello {{TWITTER}} call me on {{PHONE}}.",
            },
            scrubadub.clean_documents(
                {
                    "first.txt": "This is a test message for example@exampe.com",
                    "second.txt": "Hello @Jane call me on +33 4 41 26 62 36.",
                },
            ),
        )

    def test_list_filth(self):
        """Test the top level list_filth api"""
        filths = scrubadub.list_filth("This is a test message for example@example.com")
        self.assertEqual(
            [scrubadub.filth.EmailFilth(text='example@example.com', detector_name='email', beg=27, end=46)],
            filths,
        )

    def test_list_filth_docuemnts(self):
        """Test the top level list_filth_documents api"""
        filths = scrubadub.list_filth_documents(
            {
                "first.txt": "This is a test message for example@example.com",
                "second.txt": "Hello @Jane call me on +33 4 41 26 62 36.",
            }
        )
        self.assertEqual(
            scrubadub.Scrubber._sort_filths([
                scrubadub.filth.EmailFilth(
                    text='example@example.com', document_name='first.txt', detector_name='email', beg=27, end=46
                ),
                scrubadub.filth.TwitterFilth(
                    text='@Jane', document_name='second.txt', detector_name='twitter', beg=6, end=11
                ),
                scrubadub.filth.PhoneFilth(
                    text='+33 4 41 26 62 36', document_name='second.txt', detector_name='phone', beg=23, end=40
                ),
            ]),
            scrubadub.Scrubber._sort_filths(filths),
        )

    def test_quickstart(self):
        """Test the example given in the quick start docs"""
        text = "My cat can be contacted on example@example.com, or 1800 555-5555"
        self.assertEqual(
            'My cat can be contacted on {{EMAIL}}, or {{PHONE}}',
            scrubadub.clean(text),
        )
