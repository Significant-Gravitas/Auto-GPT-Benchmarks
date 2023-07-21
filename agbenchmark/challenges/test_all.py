import glob
import importlib
import sys
import types
from pathlib import Path
from collections import deque
from typing import Any, Dict, Optional

import pytest

from agbenchmark.challenge import Challenge
from agbenchmark.start_benchmark import CURRENT_DIRECTORY, get_regression_data
from agbenchmark.utils import replace_backslash
from agbenchmark.challenges.data_types import SuiteConfig, ChallengeData


def get_test_path(json_file: str) -> str:
    path = Path(json_file)

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


def create_single_test(
    data: Dict[str, Any] | ChallengeData,
    challenge_location: str,
    suite_config: Optional[SuiteConfig] = None,
) -> None:
    challenge_data = None
    artifacts_location = None
    if isinstance(data, ChallengeData):
        challenge_data = data
        data = data.get_data()

    # Define test class dynamically
    challenge_class = types.new_class(data["name"], (Challenge,))

    clean_challenge_location = get_test_path(challenge_location)
    setattr(challenge_class, "CHALLENGE_LOCATION", clean_challenge_location)

    # if its a parallel run suite we just give it the data
    if suite_config and suite_config.same_task:
        artifacts_location = str(Path(challenge_location).resolve())
        if "--test" in sys.argv:
            artifacts_location = str(Path(challenge_location).resolve().parent)
        setattr(
            challenge_class,
            "_data_cache",
            {clean_challenge_location: challenge_data},
        )

    setattr(
        challenge_class,
        "ARTIFACTS_LOCATION",
        artifacts_location or str(Path(challenge_location).resolve().parent),
    )

    # Define test method within the dynamically created class
    def test_method(self, config: Dict[str, Any], request) -> None:  # type: ignore
        cutoff = self.data.cutoff or 60
        self.setup_challenge(config, cutoff)

        scores = self.get_scores(config)
        request.node.scores = scores  # store scores in request.node

        assert 1 in scores["values"]

    # Parametrize the method here
    test_method = pytest.mark.parametrize(
        "challenge_data",
        [data],
        indirect=True,
    )(test_method)

    setattr(challenge_class, "test_method", test_method)

    # Attach the new class to a module so it can be discovered by pytest
    module = importlib.import_module(__name__)
    setattr(module, data["name"], challenge_class)


def create_challenge(
    data: Dict[str, Any],
    json_file: str,
    suite_config: SuiteConfig | None,
    json_files: deque,
) -> deque:
    path = Path(json_file).resolve()
    if suite_config is not None:
        grandparent_dir = path.parent.parent

        # if its a single test running we dont care about the suite
        if "--test" in sys.argv:
            create_single_test(
                data,
                str(path),
            )

            return json_files

        # Get all data.json files within the grandparent directory
        suite_files = suite_config.get_data_paths(grandparent_dir)

        # Remove all data.json files from json_files list, except for current_file
        json_files = deque(
            file for file in json_files if file not in suite_files and file != json_file
        )

        suite_file_datum = [
            ChallengeData.get_json_from_path(suite_file)
            for suite_file in suite_files
            if suite_file != json_file
        ]

        file_datum = [data, *suite_file_datum]

        if suite_config.same_task:
            challenge_data = suite_config.challenge_from_datum(file_datum)

            create_single_test(
                challenge_data, str(grandparent_dir), suite_config=suite_config
            )
        else:
            # create the individual tests
            for file_data in file_datum:
                create_single_test(file_data, str(path))

    else:
        create_single_test(data, str(path))

    return json_files


# if there's any suite.json files with that prefix


def generate_tests() -> None:  # sourcery skip: invert-any-all
    print("Generating tests...")

    json_files = deque(glob.glob(f"{CURRENT_DIRECTORY}/**/data.json", recursive=True))
    regression_tests = get_regression_data()

    # for suites to know if the file has already been used to generate the tests
    # Dynamic class creation
    while json_files:
        json_file = (
            json_files.popleft()
        )  # Take and remove the first element from json_files
        data = ChallengeData.get_json_from_path(json_file)
        suite_config = SuiteConfig.suite_data_if_suite(Path(json_file))

        commands = sys.argv
        # --category flag
        if "--category" in commands and data.get("category", "") not in commands:
            # checking if the category is retrieved from the suite
            if not suite_config or not set(suite_config.shared_category).intersection(
                commands
            ):
                continue

        # --test flag, only run the test if it's the exact one specified
        if "--test" in commands and data["name"] not in commands:
            continue

        # --maintain flag
        if "--maintain" in commands and not regression_tests.get(data["name"], None):
            continue
        elif "--improve" in commands and regression_tests.get(data["name"], None):
            continue

        # "--suite flag
        if "--suite" in commands:
            if not suite_config:
                # not a test from a suite
                continue
            elif (
                not any(command in data["name"] for command in commands)
                and suite_config.prefix not in data["name"]
            ):
                # a part of the suite but not the one specified
                continue

        json_files = create_challenge(data, json_file, suite_config, json_files)

        print(f"Generated test for {data['name']}.")


generate_tests()
