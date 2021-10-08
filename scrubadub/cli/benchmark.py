
import click

from .benchmark_time import time
from .benchmark_profile import profile
from .benchmark_accuracy import accuracy

@click.group()
def benchmark():
    """Determine how well or how quickly detectors run."""
    pass

benchmark.add_command(time)
benchmark.add_command(profile)
benchmark.add_command(accuracy)
