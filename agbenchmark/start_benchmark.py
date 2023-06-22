import click
import pytest
import json
import os


@click.group()
def cli():
    pass


@cli.command()
@click.option("--challenge", default=None, help="Specific challenge to run")
@click.option("--noreg", is_flag=True, help="Skip regression tests")
def start(challenge, noreg):
    """Start the benchmark tests. If a challenge flag is is provided, run the challenges with that mark."""
    with open("agbenchmark/config.json", "r") as f:
        config = json.load(f)

    print("Current configuration:")
    for key, value in config.items():
        print(f"{key}: {value}")

    update_config = click.confirm(
        "\nDo you want to update these parameters?", default=False
    )
    if update_config:
        config["hostname"] = click.prompt(
            "\nPlease enter a new hostname", default=config["hostname"]
        )
        config["port"] = click.prompt("Please enter a new port", default=config["port"])
        config["workspace"] = click.prompt(
            "Please enter a new workspace path", default=config["workspace"]
        )

        with open("agbenchmark/config.json", "w") as f:
            json.dump(config, f)

    print("Starting benchmark tests...", challenge)
    pytest_args = ["agbenchmark", "-vs"]
    if challenge:
        pytest_args.extend(
            ["-m", challenge]
        )  # run challenges that are of a specific marker
        if noreg:
            pytest_args.extend(
                ["-k", "not regression"]
            )  # run challenges that are of a specific marker but don't include regression challenges
        print(
            f"Running {'non-regression' + challenge if noreg else challenge} challenges"
        )
    else:
        if noreg:
            print("Running all non-regression challenges")
            pytest_args.extend(
                ["-k", "not regression"]
            )  # run challenges that are not regression challenges
        else:
            print("Running all challenges")  # run all challenges

    # Run pytest with the constructed arguments
    pytest.main(pytest_args)


if __name__ == "__main__":
    start()
