import requests
import pytest
import os

import json


class Challenge(object):
    def __init__(self, json_data):
        self.json_data = json_data

    @classmethod
    def from_json_file(cls, json_file):
        with open(json_file) as f:
            json_data = json.load(f)
        return cls(json_data)


# Playing with abstraction

# @pytest.fixture
# def server_response(request, config):
#     task = request.param  # The task is passed in indirectly
#     print(f"Server starting at {request.module}")
#     response = requests.post(
#         f"{config['url']}:{config['hostname']}", data={"task": task}
#     )
#     assert (
#         response.status_code == 200
#     ), f"Request failed with status code {response.status_code}"


# @pytest.mark.usefixtures("server_response")
# class TestChallenge(object):
#     pass


# class TestRetrievalChallenge(TestChallenge):

#     @pytest.fixture
#     def retrieve_info(self):
#         pass


# individual tests just pass the parameterization to the server_response fixture
@pytest.mark.parametrize(
    "server_response",
    [
        "create a filed call file_to_check.txt in the workspace and do nothing else"
    ],  # VARIABLE
    indirect=True,
)
@pytest.mark.basic_abilities  # VARIABLE
def test_file_in_workspace(workspace):  # VARIABLE
    assert os.path.exists(os.path.join(workspace, "file_to_check.txt"))
