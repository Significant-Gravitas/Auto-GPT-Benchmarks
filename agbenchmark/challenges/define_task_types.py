from pydantic import BaseModel
from typing import List, Optional
import json
import os


class Ground(BaseModel):
    answer: str
    should_contain: Optional[List[str]]
    should_not_contain: Optional[List[str]]
    files: List[str]


class Challenge(BaseModel):
    category: str
    task: str
    ground: Ground
    difficulty: str
    mock_func: Optional[str] = None

    def serialize(self, path: str) -> None:
        with open(path, "w") as file:
            file.write(self.json())

    @staticmethod
    def deserialize(path: str) -> "Challenge":
        print("Deserializing", path)
        with open(path, "r") as file:
            data = json.load(file)
        return Challenge(**data)
