#!/usr/bin/env python3

import sys
import timeit

from scrubadub.comparison import make_fake_document


def main():
    doc, _ = make_fake_document(paragraphs=20, seed=1234)
    variables = {'doc': doc}
    setup_cmd = 'import scrubadub; scrubber = scrubadub.Scrubber()'
    cmd = 'scrubber.clean(doc)'

    print("Timing '{}':".format(cmd))
    repeats = 100
    timer = timeit.Timer(cmd, setup=setup_cmd, globals=variables)
    try:
        time = timer.timeit(number=repeats)
    except Exception:
        timer.print_exc()
        sys.exit(1)
    else:
        print("{: >8.4f}s total runtime".format(time))
        print("{: >8.4f}s per iteration".format(time/repeats))
    sys.exit(0)


if __name__ == "__main__":
    main()
