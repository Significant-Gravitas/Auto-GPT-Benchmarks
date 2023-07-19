import glob
import importlib
import json
import os
import sys
import types
from pathlib import Path
from typing import Any, Dict

import pytest

from agbenchmark.challenge import Challenge
from agbenchmark.start_benchmark import CURRENT_DIRECTORY, get_regression_data
from agbenchmark.utils import replace_backslash
from agbenchmark.challenges.data_types import SuiteConfig

json_files = glob.glob(f"{CURRENT_DIRECTORY}/**/data.json", recursive=True)


def get_test_path(json_file: str) -> str:
    abs_location = os.path.dirname(os.path.abspath(json_file))

    path = Path(abs_location)

    # Find the index of "agbenchmark" in the path parts
    try:
        agbenchmark_index = path.parts.index("agbenchmark")
    except ValueError:
        raise ValueError("Invalid challenge location.")

    # Create the path from "agbenchmark" onwards
    challenge_location = Path(*path.parts[agbenchmark_index:])

    formatted_location = replace_backslash(str(challenge_location))
    if isinstance(formatted_location, str):
        return formatted_location
    else:
        return str(challenge_location)


# if there's any suite.json files with that prefix


def generate_tests() -> None:  # sourcery skip: invert-any-all
    print("Generating tests...")

    regression_tests = get_regression_data()
    # Dynamic class creation
    for json_file in json_files:
        with open(json_file, "r") as f:
            data = json.load(f)

            class_name = data.get("name", "")

        commands = sys.argv
        # --category flag
        if "--category" in commands and data.get("category", "") not in commands:
            print('data.get("category", "")', data.get("category", ""))
            suite_config = SuiteConfig.suite_data_if_suite(Path(json_file))
            print("suite_config", data.get("category", ""), suite_config)
            if not suite_config or not set(suite_config.shared_category).intersection(
                commands
            ):
                continue

        # --test flag
        if "--test" in commands and not any(
            command in data["name"] for command in commands
        ):
            continue

        # --maintain flag
        if "--maintain" in commands and not regression_tests.get(data["name"], None):
            continue
        elif "--improve" in commands and regression_tests.get(data["name"], None):
            continue

        challenge_location = get_test_path(json_file)

        # Define test class dynamically
        challenge_class = types.new_class(class_name, (Challenge,))

        setattr(challenge_class, "CHALLENGE_LOCATION", challenge_location)

        # Define test method within the dynamically created class
        def test_method(self, config: Dict[str, Any]) -> None:  # type: ignore
            cutoff = self.data.cutoff or 60
            self.setup_challenge(config, cutoff)

            scores = self.get_scores(config)

            assert 1 in scores

        # Parametrize the method here
        test_method = pytest.mark.parametrize(
            "challenge_data",
            [data],
            indirect=True,
        )(test_method)

        setattr(challenge_class, "test_method", test_method)

        # Attach the new class to a module so it can be discovered by pytest
        module = importlib.import_module(__name__)
        setattr(module, class_name, challenge_class)

        print(f"Generated test for {class_name}.")


generate_tests()
