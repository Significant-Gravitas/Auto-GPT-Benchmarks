import json
from enum import Enum
from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel, validator


class DifficultyLevel(Enum):
    interface = "interface"
    basic = "basic"
    novice = "novice"
    intermediate = "intermediate"
    advanced = "advanced"
    expert = "expert"
    human = "human"


# map from enum to difficulty level (numeric)
DIFFICULTY_MAP = {
    DifficultyLevel.interface: 1,
    DifficultyLevel.basic: 2,
    DifficultyLevel.novice: 3,
    DifficultyLevel.intermediate: 4,
    DifficultyLevel.advanced: 5,
    DifficultyLevel.expert: 6,
    DifficultyLevel.human: 7,
}


class Info(BaseModel):
    difficulty: DifficultyLevel
    description: str
    side_effects: List[str]

    @validator("difficulty", pre=True)
    def difficulty_to_enum(cls: "Info", v: str | DifficultyLevel) -> DifficultyLevel:
        """Convert a string to an instance of DifficultyLevel."""
        if isinstance(v, DifficultyLevel):
            return v

        if isinstance(v, str):
            try:
                return DifficultyLevel(v.lower())
            except ValueError:
                pass

        raise ValueError(f"Cannot convert {v} to DifficultyLevel.")


class Ground(BaseModel):
    answer: str
    should_contain: Optional[List[str]] = None
    should_not_contain: Optional[List[str]] = None
    files: List[str]
    type: str


class ChallengeData(BaseModel):
    name: str
    category: List[str]
    task: str
    dependencies: List[str]
    cutoff: int
    ground: Ground
    info: Info

    def serialize(self, path: str) -> None:
        with open(path, "w") as file:
            file.write(self.json())

    @staticmethod
    def deserialize(path: str) -> "ChallengeData":
        # this script is in root/agbenchmark/challenges/define_task_types.py
        script_dir = Path(__file__).resolve().parent.parent.parent
        json_path = script_dir / Path(path)

        print("Deserializing", path)

        with open(json_path, "r") as file:
            data = json.load(file)

        # validation and loading data from suite.json
        if suite_config := SuiteConfig.suite_data_if_suite(json_path):
            if data.get("category") is None:
                data["category"] = suite_config.shared_category
            else:
                data["category"] = suite_config.shared_category + data["category"]

            if data.get("dependencies") is None:
                data["dependencies"] = suite_config.dependencies
            else:
                data["dependencies"] = suite_config.dependencies + data["dependencies"]

            assert suite_config.prefix in data["name"]

        if data.get("category") is None:
            raise ValueError(f"Category not found in {path}")

        return ChallengeData(**data)


class SuiteConfig(BaseModel):
    same_task: bool
    reverse_order: bool
    prefix: str
    dependencies: List[str]
    shared_category: List[str]
    children: Optional[List[ChallengeData]] = None

    @staticmethod
    def suite_data_if_suite(json_path: Path) -> Optional["SuiteConfig"]:
        """Return the suite data if the path is in a suite."""
        if SuiteConfig.check_if_suite(json_path):
            return SuiteConfig.deserialize_from_test_data(json_path)
        else:
            return None

    @staticmethod
    def check_if_suite(json_path: Path) -> bool:
        """Check if the json file is in a suite."""

        # if its in a suite, suite.json is in the parent suite/suite.json & 1_challenge/data.json
        suite_path = json_path.parent.parent / "suite.json"

        # validation and loading data from suite.json
        return suite_path.exists()

    @staticmethod
    def deserialize_from_test_data(data_path: Path) -> "SuiteConfig":
        suite_path = data_path.parent.parent / "suite.json"

        """Deserialize from a children path when children and order of children does not matter."""
        print("Deserializing suite", data_path)

        with open(suite_path, "r") as file:
            data = json.load(file)
        return SuiteConfig(**data)

    @staticmethod
    def deserialize(path: str) -> "SuiteConfig":
        """Used to generate tests when children and order of children matters."""

        # this script is in root/agbenchmark/challenges/data_types.py
        script_dir = Path(__file__).resolve().parent.parent.parent
        path = str(script_dir / path)

        print("Deserializing suite", path)

        with open(path, "r") as file:
            data = json.load(file)
        return SuiteConfig(**data)
