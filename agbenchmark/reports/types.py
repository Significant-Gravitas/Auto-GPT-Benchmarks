from dataclasses import dataclass
from typing import Optional, Dict, List


@dataclass
class Metrics:
    difficulty: str
    success: bool
    success_percentage: float
    run_time: str
    fail_reason: Optional[str] = None


@dataclass
class Test:
    data_path: str
    is_regression: bool
    category: List[str]
    task: str
    answer: str
    description: str
    metrics: Metrics
    reached_cutoff: bool


@dataclass
class Tests:
    tests: Dict[str, Test]


@dataclass
class MetricsOverall:
    run_time: str
    highest_difficulty: str


@dataclass
class Report:
    command: str
    completion_time: str
    metrics: MetricsOverall
    tests: Tests
    config: Dict[str, str]
