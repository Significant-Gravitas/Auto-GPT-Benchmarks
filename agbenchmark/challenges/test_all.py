import json
import os
import importlib
import types
import glob
from typing import Any, Dict
import pytest
from pathlib import Path
from dotenv import load_dotenv

from agbenchmark.start_benchmark import (
    get_regression_data,
)
from agbenchmark.challenge import Challenge

load_dotenv()

IMPROVE = os.getenv("IMPROVE", "False")


json_files = glob.glob("agbenchmark/challenges/**/data.json", recursive=True)


def get_test_path(json_file):
    abs_location = os.path.dirname(os.path.abspath(json_file))

    path = Path(abs_location)

    # Find the index of "agbenchmark" in the path parts
    try:
        agbenchmark_index = path.parts.index("agbenchmark")
    except ValueError:
        raise ValueError("Invalid challenge location.")

    # Create the path from "agbenchmark" onwards
    challenge_location = Path(*path.parts[agbenchmark_index:])

    return str(challenge_location)


def generate_tests():
    print("generating")
    print("config exists")
    # Dynamic class creation
    for json_file in json_files:
        with open(json_file, "r") as f:
            data = json.load(f)

            class_name = data.get("name", "")

        print("class_name", class_name)

        challenge_location = get_test_path(json_file)

        print("challenge_location", challenge_location)

        # Define test class dynamically
        challenge_class = types.new_class(class_name, (Challenge,))

        print("challenge_class", challenge_class)
        setattr(challenge_class, "CHALLENGE_LOCATION", challenge_location)

        print("challenge_class.CHALLENGE_LOCATION", challenge_class.CHALLENGE_LOCATION)

        # Define test method within the dynamically created class
        def test_method(self, config: Dict[str, Any]) -> None:
            self.setup_challenge(config)

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
        print("module", module)
        setattr(module, class_name, challenge_class)


generate_tests()
