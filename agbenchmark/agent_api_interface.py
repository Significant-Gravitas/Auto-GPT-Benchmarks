import os
import time
from typing import Any, Dict

from agent_protocol_client import AgentApi, ApiClient, Configuration, TaskRequestBody

from agbenchmark.utils.data_types import ChallengeData


async def run_api_agent(
    task: ChallengeData, config: Dict[str, Any], timeout: int
) -> None:
    configuration = Configuration(host=config["host"])
    async with ApiClient(configuration) as api_client:
        api_instance = AgentApi(api_client)
        task_request_body = TaskRequestBody(input=task.task)

        start_time = time.time()
        response = await api_instance.create_agent_task(
            task_request_body=task_request_body
        )
        task_id = response.task_id

        i = 1
        while step := await api_instance.execute_agent_task_step(task_id=task_id):
            print(f"[{task.name}] - step {step.name} ({i}. request)")
            i += 1

            if step.is_last:
                break

            if time.time() - start_time > timeout:
                raise TimeoutError("Time limit exceeded")

        artifacts = await api_instance.list_agent_task_artifacts(task_id=task_id)
        for artifact in artifacts:
            path = os.path.join(
                config["workspace"], artifact.relative_path, artifact.file_name
            )
            with open(path, "wb") as f:
                content = await api_instance.download_agent_task_artifact(
                    task_id=task_id, artifact_id=artifact.artifact_id
                )
                f.write(content)
