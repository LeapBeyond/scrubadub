
from typing import Union, List, Dict, Sequence

# convenient imports
from .scrubbers import Scrubber
from . import filth
from . import detectors
from . import post_processors
from .filth import Filth

__version__ = VERSION = "1.2.2"
__all__ = [
    'Scrubber', 'filth', 'detectors', 'post_processors', 'clean', 'clean_documents', 'list_filth',
    'list_filth_documents',
]


def clean(text: str, **kwargs) -> str:
    """Seaches for `Filth` in `text` in a string and replaces it with placeholders.

    .. code:: pycon

        >>> import scrubadub
        >>> scrubadub.clean(u"contact Joe Duffy at joe@example.com")
        'contact {{NAME}} {{NAME}} at {{EMAIL}}'

    :param text: The text containing possible PII that needs to be redacted
    :type text: `str`
    :return: Text with all `Filth` replaced.
    :rtype: `str`

    """
    scrubber = Scrubber()
    return scrubber.clean(text, **kwargs)


def clean_documents(documents: Union[List[str], Dict[str, str]], **kwargs) -> Union[Sequence[str], Dict[str, str]]:
    """Seaches for `Filth` in `documents` and replaces it with placeholders.

    `documents` can be in a dict, in the format of ``{'document_name': 'document'}``, or as a list of strings
    (each a seperate document).
    This can be useful when processing many documents.

    .. code:: pycon

        >>> import scrubadub
        >>> scrubadub.clean_documents({'contact.txt': "contact Joe Duffy at joe@example.com",
        ...     'hello.txt': 'hello world!'})
        {'contact.txt': 'contact {{NAME}} {{NAME}} at {{EMAIL}}', 'hello.txt': 'hello world!'}

        >>> scrubadub.clean_documents(["contact Joe Duffy at joe@example.com", 'hello world!'])
        ['contact {{NAME}} {{NAME}} at {{EMAIL}}', 'hello world!']

    :param documents: Documents containing possible PII that needs to be redacted in the form of a list of documents
        or a dictonary with the key as the document name and the value as the document text
    :type documents: `list` of `str` objects, `dict` of `str` objects
    :return: Documents in the same format as input, but with `Filth` redacted
    :rtype: `list` of `str` objects, `dict` of `str` objects; same as input
    """
    scrubber = Scrubber()
    return scrubber.clean_documents(documents, **kwargs)


def list_filth(text: str, **kwargs) -> List[Filth]:
    """Return a list of `Filth` that was detected in the string `text`.

    .. code:: pycon

        >>> import scrubadub
        >>> scrubadub.list_filth(u"contact Joe Duffy at joe@example.com")
        [<NameFilth text='Joe' detector_name='name'>,
         <NameFilth text='Duffy' detector_name='name'>,
         <EmailFilth text='joe@example.com' detector_name='email'>]

    :param text: The text containing possible PII that needs to be found
    :type text: `str`
    :return: A list of all the `Filth` objects that were found
    :rtype: `list` of `Filth` objects

    """
    scrubber = Scrubber()
    return list(scrubber.iter_filth(text, **kwargs))


def list_filth_documents(documents: Union[List[str], Dict[str, str]], **kwargs) -> List[Filth]:
    """Return a list of `Filth` that was detected in the string `text`.

    `documents` can be in a dict, in the format of ``{'document_name': 'document'}``, or as a list of strings
    (each a seperate document).
    This can be useful when processing many documents.

    .. code:: pycon

        >>> import scrubadub
        >>> scrubadub.list_filth_documents({'contact.txt': "contact Joe Duffy at joe@example.com",
        ...     'hello.txt': 'hello world!'})
        [<NameFilth text='Joe' document_name='contact.txt' detector_name='name'>,
         <NameFilth text='Duffy' document_name='contact.txt' detector_name='name'>,
         <EmailFilth text='joe@example.com' document_name='contact.txt' detector_name='email'>]

        >>> scrubadub.list_filth_documents(["contact Joe Duffy at joe@example.com", 'hello world!'])
        [<NameFilth text='Joe' document_name='0' detector_name='name'>,
         <NameFilth text='Duffy' document_name='0' detector_name='name'>,
         <EmailFilth text='joe@example.com' document_name='0' detector_name='email'>]

    :param documents: Documents containing possible PII that needs to be found in the form of a list of documents
        or a dictonary with the key as the document name and the value as the document text
    :type documents: `list` of `str` objects, `dict` of `str` objects
    :return: A list of all the `Filth` objects that were found
    :rtype: `list` of `Filth` objects

    """
    scrubber = Scrubber()
    return list(scrubber.iter_filth_documents(documents, **kwargs))
