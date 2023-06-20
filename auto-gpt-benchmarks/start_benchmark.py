import click
import pytest
import json


@click.command()
@click.option("--challenge", default=None, help="Specific challenge to run")
def start(challenge):
    """Start the benchmark tests. If a challenge flag is is provided, run the challenges with that mark."""
    with open("config.json", "r") as f:
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

        with open("config.json", "w") as f:
            json.dump(config, f)

    if challenge:
        pytest.main(["-m", challenge])
    else:
        pytest.main()


if __name__ == "__main__":
    start()
