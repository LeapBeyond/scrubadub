
from typing import Union, List, Dict, Sequence, Optional

# convenient imports
from .scrubbers import Scrubber
from . import filth
from . import detectors
from . import post_processors
from .filth import Filth

__version__ = VERSION = "2.0.0.rc0"
__all__ = [
    'Scrubber', 'filth', 'detectors', 'post_processors', 'clean', 'clean_documents', 'list_filth',
    'list_filth_documents',
]


def clean(text: str, locale: Optional[str] = None, **kwargs) -> str:
    """Seaches for ``Filth`` in `text` in a string and replaces it with placeholders.

    .. code:: pycon

        >>> import scrubadub
        >>> scrubadub.clean(u"contact me at joe@example.com")
        'contact me at {{EMAIL}}'

    :param text: The text containing possible PII that needs to be redacted
    :type text: `str`
    :param locale: The locale of the documents in the format: 2 letter lower-case language code followed by an
                   underscore and the two letter upper-case country code, eg "en_GB" or "de_CH"
    :type locale: str
    :return: Text with all :class:``Filth`` replaced.
    :rtype: `str`

    """
    scrubber = Scrubber(locale=locale)
    return scrubber.clean(text, **kwargs)


def clean_documents(documents: Union[Sequence[str], Dict[Optional[str], str]], locale: Optional[str] = None, **kwargs
                    ) -> Union[Sequence[str], Dict[Optional[str], str]]:
    """Seaches for ``Filth`` in `documents` and replaces it with placeholders.

    `documents` can be in a dict, in the format of ``{'document_name': 'document'}``, or as a list of strings
    (each a seperate document).
    This can be useful when processing many documents.

    .. code:: pycon

        >>> import scrubadub
        >>> scrubadub.clean_documents({'contact.txt': "contact me at joe@example.com",
        ...     'hello.txt': 'hello world!'})
        {'contact.txt': 'contact me at {{EMAIL}}', 'hello.txt': 'hello world!'}

        >>> scrubadub.clean_documents(["contact me at joe@example.com", 'hello world!'])
        ['contact me at {{EMAIL}}', 'hello world!']

    :param documents: Documents containing possible PII that needs to be redacted in the form of a list of documents
        or a dictonary with the key as the document name and the value as the document text
    :type documents: `list` of `str` objects, `dict` of `str` objects
    :param locale: The locale of the documents in the format: 2 letter lower-case language code followed by an
                   underscore and the two letter upper-case country code, eg "en_GB" or "de_CH"
    :type locale: str
    :return: Documents in the same format as input, but with `Filth` redacted
    :rtype: `list` of `str` objects, `dict` of `str` objects; same as input
    """
    scrubber = Scrubber(locale=locale)
    return scrubber.clean_documents(documents, **kwargs)


def list_filth(text: str, locale: Optional[str] = None, **kwargs) -> List[Filth]:
    """Return a list of ``Filth`` that was detected in the string `text`.

    .. code:: pycon

        >>> import scrubadub
        >>> scrubadub.list_filth(u"contact me at joe@example.com")
        [<EmailFilth text='joe@example.com' beg=14 end=29 detector_name='email' locale='en_US'>]

    :param text: The text containing possible PII that needs to be found
    :type text: `str`
    :param locale: The locale of the documents in the format: 2 letter lower-case language code followed by an
                   underscore and the two letter upper-case country code, eg "en_GB" or "de_CH"
    :type locale: str
    :return: A list of all the :class:``Filth`` objects that were found
    :rtype: `list` of :class:``Filth`` objects

    """
    scrubber = Scrubber(locale=locale)
    return list(scrubber.iter_filth(text, **kwargs))


def list_filth_documents(documents: Union[List[str], Dict[Optional[str], str]], locale: Optional[str] = None,
                         **kwargs) -> List[Filth]:
    """Return a list of ``Filth`` that was detected in the string `text`.

    `documents` can be in a dict, in the format of ``{'document_name': 'document'}``, or as a list of strings
    (each a seperate document).
    This can be useful when processing many documents.

    .. code:: pycon

        >>> import scrubadub
        >>> scrubadub.list_filth_documents(
        ...     {'contact.txt': "contact me at joe@example.com", 'hello.txt': 'hello world!'}
        ... )
        [<EmailFilth text='joe@example.com' document_name='contact.txt' beg=14 end=29 detector_name='email' \
locale='en_US'>]

        >>> scrubadub.list_filth_documents(["contact me at joe@example.com", 'hello world!'])
        [<EmailFilth text='joe@example.com' document_name='0' beg=14 end=29 detector_name='email' locale='en_US'>]

    :param documents: Documents containing possible PII that needs to be found in the form of a list of documents
        or a dictonary with the key as the document name and the value as the document text
    :type documents: `list` of `str` objects, `dict` of `str` objects
    :param locale: The locale of the documents in the format: 2 letter lower-case language code followed by an
                   underscore and the two letter upper-case country code, eg "en_GB" or "de_CH"
    :type locale: str
    :return: A list of all the :class:``Filth`` objects that were found
    :rtype: `list` of :class:``Filth`` objects

    """
    scrubber = Scrubber(locale=locale)
    return list(scrubber.iter_filth_documents(documents, **kwargs))
