import os
import shutil

from agent_protocol_client import AgentApi, ApiClient, Configuration, TaskRequestBody
from dotenv import load_dotenv

from agbenchmark.start_benchmark import CURRENT_DIRECTORY

load_dotenv()

mock_test_str = os.getenv("MOCK_TEST")
MOCK_FLAG = mock_test_str.lower() == "true" if mock_test_str else False


configuration = Configuration(host="http://localhost:8000")


async def run_agent(task: str):
    async with ApiClient(configuration) as api_client:
        api_instance = AgentApi(api_client)
        task_request_body = TaskRequestBody(input=task)

        response = await api_instance.create_agent_task(
            task_request_body=task_request_body
        )
        task_id = response.task_id

        i = 1
        while (
            step := await api_instance.execute_agent_task_step(task_id=task_id)
        ) and step.is_last is False:
            print(f"{i}. request finished")
            i += 1


def copy_artifacts_into_workspace(
    workspace: str, artifact_folder_name: str, challenge_dir_path: str
) -> None:
    # this file is at agbenchmark\agent_interface.py
    source_dir = os.path.join(
        CURRENT_DIRECTORY, "..", challenge_dir_path, artifact_folder_name
    )

    # Check if source_dir exists, if not then return immediately.
    if not os.path.exists(source_dir):
        return

    for file_name in os.listdir(source_dir):
        full_file_name = os.path.join(source_dir, file_name)
        if os.path.isfile(full_file_name):
            shutil.copy(full_file_name, workspace)
