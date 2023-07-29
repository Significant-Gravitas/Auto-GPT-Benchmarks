from dataclasses import dataclass
from typing import Optional, Dict, List


@dataclass
class Metrics:
    difficulty: str
    success: bool
    success_percent: float
    run_time: Optional[str] = None
    fail_reason: Optional[str] = None


@dataclass
class MetricsOverall:
    run_time: str
    highest_difficulty: str
    percentage: Optional[float] = None


@dataclass
class Test:
    data_path: str
    is_regression: bool
    answer: str
    description: str
    metrics: Metrics
    category: Optional[List[str]] = None
    task: Optional[str] = None
    reached_cutoff: Optional[bool] = None


@dataclass
class SuiteTest:
    data_path: str
    category: Optional[List[str]]
    metrics: MetricsOverall
    tests: Dict[str, Test]
    task: Optional[str] = None
    reached_cutoff: Optional[bool] = None


@dataclass
class Report:
    command: str
    completion_time: str
    metrics: MetricsOverall
    tests: Dict[str, Test]
    config: Dict[str, str]
