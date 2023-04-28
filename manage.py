import pathlib

import click


@click.group()
def cli(): pass


@cli.command()
@click.argument("settings", click.Path)
def evaluate(settings: pathlib.Path):
    ...


if __name__ == "__main__":
    cli()