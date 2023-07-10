import json
import time
from datetime import datetime
from typing import Any, Dict
import os


class ReportManager:
    """Abstracts interaction with the regression tests file"""

    def __init__(self, filename: str):
        self.filename = filename
        self.start_time = time.time()
        self.load()

    def load(self) -> None:
        try:
            with open(self.filename, "r") as f:
                file_content = (
                    f.read().strip()
                )  # read the content and remove any leading/trailing whitespace
                if file_content:  # if file is not empty, load the json
                    self.tests = json.loads(file_content)
                else:  # if file is empty, assign an empty dictionary
                    self.tests = {}
        except FileNotFoundError:
            self.tests = {}
        except json.decoder.JSONDecodeError:  # If JSON is invalid
            self.tests = {}
        self.save()

    def save(self) -> None:
        with open(self.filename, "w") as f:
            json.dump(self.tests, f, indent=4)

    def add_test(self, test_name: str, test_details: dict) -> None:
        self.tests[test_name] = test_details
        self.save()

    def remove_test(self, test_name: str) -> None:
        if test_name in self.tests:
            del self.tests[test_name]
            self.save()

    def end_info_report(self, config: Dict[str, Any]) -> None:
        self.tests = {
            "tests": self.tests,
            "current_time": datetime.now().isoformat(),
            "time_elapsed": time.time() - self.start_time,
            "config": config,
        }

        self.save()
