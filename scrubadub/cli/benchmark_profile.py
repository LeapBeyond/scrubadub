import subprocess
import sys
import click
import pstats
import tempfile
import cProfile
from click.utils import LazyFile
from typing import Optional

import scrubadub
from scrubadub.comparison import make_fake_document


@click.command()
@click.option('--detector-list', type=str, default=None, help='Comma seperated list of detectors to run.')
@click.option('--n_paragraphs', type=int, default=20, show_default=True, help='Number of paragraphs to generate.')
@click.option('--stats', is_flag=True, help='Print profiling stats.')
@click.option('--seed', type=int, default=1234, show_default=True, help='Seed used to create text.')
@click.option('--output', type=click.File('wb'), default=None, help='Location to save profile stats to.')
@click.option('--kcachegrind', is_flag=True, help='Open kcachegrind to display the result.')
def profile(n_paragraphs: int = 20, seed: int = 1234, detector_list: Optional[str] = None,
            output: Optional[LazyFile] = None, kcachegrind: bool = False, stats: bool = True):
    """Profile the scrubbing porcess with cProfile."""
    doc, _ = make_fake_document(paragraphs=n_paragraphs, seed=seed)

    if isinstance(detector_list, str):
        detector_list = [x.strip() for x in detector_list.split(',')]

    scrubber = scrubadub.Scrubber(detector_list=detector_list)

    print("Profiling 'scrubber.clean(doc)':")
    profiler = cProfile.Profile()
    profiler.enable()
    scrubber.clean(doc)
    profiler.disable()

    if stats:
        ps = pstats.Stats(profiler).sort_stats(pstats.SortKey.CUMULATIVE)
        ps.print_stats()

    if output is not None:
        profiler.dump_stats(output)

    if kcachegrind:
        with tempfile.NamedTemporaryFile('wb', suffix='.pyprof') as pyprof_file:
            profiler.dump_stats(pyprof_file.name)
            subprocess.run(['pyprof2calltree', '-i', pyprof_file.name, '-k'])
