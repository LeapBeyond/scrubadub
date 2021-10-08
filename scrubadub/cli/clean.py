
import click
import pathlib
from click.utils import LazyFile
from typing import Union, Sequence, Optional

from scrubadub.scrubbers import Scrubber


@click.command()
@click.option('--detector-list', type=str, default=None)
@click.option('--locale', default='en_US', help='Locale of the text.', show_default=True)
@click.option('--suffix', default='_cleaned', help='Suffix to add onto the filename.', show_default=True)
@click.argument('files', type=click.File('rt'), nargs=-1)
def clean(files: Union[LazyFile, Sequence[LazyFile]], locale: str = 'en_US', suffix: str = '_cleaned',
          detector_list: Optional[str] = None):
    """Clean text files by removing filth (PII)."""
    file_list = list(files)

    if isinstance(detector_list, str):
        scrubber = Scrubber(locale=locale, detector_list=[x.strip() for x in detector_list.split(',')])
    else:
        scrubber = Scrubber(locale=locale)

    for file in file_list:
        try:
            text = file.read()
        finally:
            file.close()

        clean_text = scrubber.clean(text)

        path = pathlib.Path(file.name)
        output_file_name = path.parent.absolute() / (path.stem + suffix + path.suffix)

        with open(output_file_name.absolute(), 'wt') as f:
            f.write(clean_text)
