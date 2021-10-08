
import click

from .benchmark import benchmark
from .clean import clean


@click.group()
def main():
    """Scrubadub helps you find and remove filth (PII) in text."""
    pass


main.add_command(benchmark)
main.add_command(clean)
