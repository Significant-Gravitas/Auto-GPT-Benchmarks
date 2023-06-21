from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Ground:
    answer: str
    should_contain: Optional[List[str]]
    should_not_contain: Optional[List[str]]
    files: List[str]


@dataclass
class Challenge:
    category: str
    task: str
    ground: Ground
    difficulty: str
