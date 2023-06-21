import json
import os
import pytest
import shutil
from agbenchmark.mocks.tests.retrieval_manual import mock_retrieval
import requests


@pytest.fixture(scope="module")
def config():
    config_file = os.path.abspath("agbenchmark/config.json")
    print(f"Config file: {config_file}")
    with open(config_file, "r") as f:
        config = json.load(f)
    return config


@pytest.fixture
def workspace(config):
    yield config["workspace"]
    # teardown after test function completes
    for filename in os.listdir(config["workspace"]):
        file_path = os.path.join(config["workspace"], filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f"Failed to delete {file_path}. Reason: {e}")


@pytest.fixture(autouse=True)
def server_response(request, config):
    task = request.param  # The task is passed in indirectly
    print(f"Server starting at {request.module}")
    # response = requests.post(
    #     f"{config['hostname']}:{config['port']}", data={"task": task}
    # )
    # assert (
    #     response.status_code == 200
    # ), f"Request failed with status code {response.status_code}"
    mock_retrieval(task, config["workspace"])


regression_txt = "agbenchmark/tests/regression/regression_tests.txt"


def pytest_runtest_makereport(item, call):
    if call.when != "call":
        return
    # Read the current regression tests
    with open(regression_txt, "r") as f:
        regression_tests = f.readlines()
    if call.excinfo is None:
        # If the test is not already in the file, write it to the file
        if f"{item.nodeid}\n" not in regression_tests:
            with open(regression_txt, "a") as f:
                f.write(f"{item.nodeid}\n")
    elif f"{item.nodeid}\n" in regression_tests:
        regression_tests.remove(f"{item.nodeid}\n")
        with open(regression_txt, "w") as f:
            f.writelines(regression_tests)


def pytest_collection_modifyitems(items):
    with open(regression_txt, "r") as f:
        regression_tests = f.readlines()
    for item in items:
        print("pytest_collection_modifyitems", item.nodeid)
        if item.nodeid + "\n" in regression_tests:
            print(regression_txt)
            item.add_marker(pytest.mark.regression)
