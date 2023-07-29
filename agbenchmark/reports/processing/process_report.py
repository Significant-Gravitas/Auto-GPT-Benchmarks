from typing import Any
import os
import json
from pathlib import Path

from agbenchmark.utils.data_types import STRING_DIFFICULTY_MAP
from agbenchmark.reports.processing.types import Report, SuiteTest
from agbenchmark.start_benchmark import REPORTS_PATH
from agbenchmark.reports.processing.get_files import get_latest_files_in_subdirectories


def get_reports_data() -> dict[str, Any]:
    latest_files = get_latest_files_in_subdirectories(REPORTS_PATH)
    print(latest_files)

    reports_data = {}

    # This will print the latest file in each subdirectory and add to the files_data dictionary
    for subdir, file in latest_files:
        subdir_name = os.path.basename(os.path.normpath(subdir))
        print(f"Subdirectory: {subdir}, Latest file: {file}")
        with open(Path(subdir) / file, "r") as f:
            # Load the JSON data from the file
            json_data = json.load(f)
            converted_data = Report.parse_obj(json_data)
            # get the last directory name in the path as key
            reports_data[subdir_name] = converted_data

    return reports_data


def get_agent_category(report: Report) -> dict[str, Any]:
    categories: dict[str, Any] = {}

    def get_highest_category_difficulty(data) -> None:
        for category in data.category:
            if category == "interface":
                continue
            num_dif = STRING_DIFFICULTY_MAP[data.metrics.difficulty]
            if num_dif > categories.setdefault(category, 0):
                categories[category] = num_dif

    for _, test_data in report.tests.items():
        if isinstance(test_data, SuiteTest):
            for _, test_data in test_data.tests.items():
                get_highest_category_difficulty(test_data)
        else:
            get_highest_category_difficulty(test_data)

    return categories


def all_agent_categories(reports_data: dict[str, Any]) -> dict[str, Any]:
    all_categories: dict[str, Any] = {}

    for name, report in reports_data.items():
        categories = get_agent_category(report)
        all_categories[name] = categories

    return all_categories
