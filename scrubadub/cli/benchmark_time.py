
import sys
import click
import timeit
from typing import Optional

from scrubadub.comparison import make_fake_document

@click.command()
@click.option('--detector-list', type=str, default=None)
@click.option('--n_paragraphs', type=int, default=20)
@click.option('--seed', type=int, default=1234)
@click.option('--repeats', type=int, default=50)
def time(n_paragraphs: int = 20, seed: int = 1234, repeats: int = 50, detector_list: Optional[str] = None, ):
    doc, _ = make_fake_document(paragraphs=n_paragraphs, seed=seed)
    variables = {'doc': doc, 'detector_list': [x.strip() for x in detector_list.split(',')]}
    setup_cmd = 'import scrubadub; scrubber = scrubadub.Scrubber(detector_list=detector_list)'
    cmd = 'scrubber.clean(doc)'

    print("Timing '{}':".format(cmd))
    timer = timeit.Timer(cmd, setup=setup_cmd, globals=variables)
    try:
        time = timer.timeit(number=repeats)
    except Exception:
        timer.print_exc()
        sys.exit(1)

    time_per_iteration = time/repeats
    print("{: >8.4f}s total runtime".format(time))
    print("{: >8.4f}s per iteration".format(time_per_iteration))

    if time_per_iteration > 0.02:
        print("Usual runtimes for the default set of detectors is 0.02s per iteration.")

    if time_per_iteration > 0.1:
        sys.exit(1)


