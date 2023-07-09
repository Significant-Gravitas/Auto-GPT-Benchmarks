import json
import os
import shutil
import importlib
import types
import glob
from pathlib import Path  # noqa
from typing import Any, Dict, Generator


import pytest

from agbenchmark.start_benchmark import (
    CONFIG_PATH,
    get_regression_data,
    REGRESSION_TESTS_PATH,
)
from agbenchmark.RegressionManager import RegressionManager
from agbenchmark.challenge import Challenge


json_files = glob.glob("agbenchmark/challenges/**/data.json", recursive=True)


def generate_tests():
    print("generating")
    print("config exists")
    # Dynamic class creation
    for json_file in json_files:
        with open(json_file, "r") as f:
            data = json.load(f)

            name = data.get("name", "")

            class_name = "Test" + name

        print("class_name", class_name)

        challenge_location = os.path.dirname(os.path.abspath(json_file))

        print("challenge_location", challenge_location)

        # Define test class dynamically
        challenge_class = types.new_class(class_name, (Challenge,))

        print("challenge_class", challenge_class)
        challenge_class.CHALLENGE_LOCATION = challenge_location

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

        regression_data = get_regression_data()

        # Here we add the dependencies and category markers dynamically
        dependencies = data.get("dependencies", [])
        # Filter dependencies if they exist in regression data
        dependencies = [
            dep for dep in dependencies if not regression_data.get(dep, None)
        ]

        challenge_class.test_method = pytest.mark.depends(on=dependencies, name=name)(
            challenge_class.test_method
        )

        categories = data.get("category", [])
        for category in categories:
            challenge_class.test_method = getattr(pytest.mark, category)(
                challenge_class.test_method
            )

        print("challenge_class.test_method", challenge_class.test_method)

        # Attach the new class to a module so it can be discovered by pytest
        module = importlib.import_module(__name__)
        print("module", module)
        setattr(module, class_name, challenge_class)


generate_tests()
