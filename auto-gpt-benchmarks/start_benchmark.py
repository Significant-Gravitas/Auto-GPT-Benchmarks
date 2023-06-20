import click
import pytest


@click.command()
@click.option("--challenge", default=None, help="Specific challenge to run")
def start(challenge):
    """Start the benchmark tests. If a challenge flag is is provided, run the challenges with that mark."""
    if challenge:
        pytest.main(["-m", challenge])
    else:
        pytest.main()


if __name__ == "__main__":
    start()
