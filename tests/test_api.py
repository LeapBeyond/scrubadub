import unittest
import scrubadub


class APITestCase(unittest.TestCase):

    def test_clean(self):
        """Test the top level clean api"""
        self.assertEqual(
            scrubadub.clean("This is a test message for example@exampe.com"),
            "This is a test message for {{EMAIL}}",
        )

    def test_clean_docuemnts(self):
        """Test the top level clean_documents api"""
        self.assertEqual(
            scrubadub.clean_documents(
                {
                    "first.txt": "This is a test message for example@exampe.com",
                    "second.txt": "Hello Jane I am Tom.",
                }
            ),
            {
                "first.txt": "This is a test message for {{EMAIL}}",
                "second.txt": "Hello {{NAME}} I am {{NAME}}.",
            }
        )

    def test_list_filth(self):
        """Test the top level list_filth api"""
        filths = scrubadub.list_filth("This is a test message for example@example.com")
        self.assertEqual(
            filths,
            [scrubadub.filth.EmailFilth(text='example@example.com', detector_name='email', beg=27, end=46)],
        )

    def test_list_filth_docuemnts(self):
        """Test the top level list_filth_documents api"""
        filths = scrubadub.list_filth_documents(
            {
                "first.txt": "This is a test message for example@example.com",
                "second.txt": "Hello Jane, I am Tom.",
            }
        )
        self.assertEqual(
            scrubadub.Scrubber._sort_filths(filths),
            scrubadub.Scrubber._sort_filths([
                scrubadub.filth.EmailFilth(
                    text='example@example.com', document_name='first.txt', detector_name='email', beg=27, end=46
                ),
                scrubadub.filth.NameFilth(text='Jane', document_name='second.txt', detector_name='name', beg=6, end=10),
                scrubadub.filth.NameFilth(text='Tom', document_name='second.txt', detector_name='name', beg=17, end=20),
            ])
        )

    def test_quickstart(self):
        """Test the example given in the quick start docs"""
        text = "My cat can be contacted on example@example.com, or 1800 555-5555"
        self.assertEqual(
            scrubadub.clean(text),
            'My cat can be contacted on {{EMAIL}}, or {{PHONE}}'
        )