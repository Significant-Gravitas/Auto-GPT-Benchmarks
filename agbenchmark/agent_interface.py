import os
import shutil
import subprocess
import sys
import threading
import time
from typing import Any, Dict, Optional

from dotenv import load_dotenv

from agbenchmark.start_benchmark import CURRENT_DIRECTORY

load_dotenv()

mock_test_str = os.getenv("MOCK_TEST")
MOCK_FLAG = mock_test_str.lower() == "true" if mock_test_str else False


class TestSubprocess:
    """A convenience class to allow creating a subprocess with a timeout while capturing its output"""

    def __init__(self, cmd: list[str]) -> None:
        self.cmd = cmd
        self.process: Optional[subprocess.CompletedProcess] = None

    def run(self, timeout: int) -> None:
        def target() -> None:
            self.process = subprocess.run(self.cmd, universal_newlines=True)

        stop_event = threading.Event()
        thread = threading.Thread(target=target)
        thread.start()

        start_time = time.time()
        while thread.is_alive():
            if time.time() - start_time > timeout:
                print(f"The agent timed out")
                stop_event.set()
                thread.join()
                break

            time.sleep(1)


def run_agent(
    task: str, config: Dict[str, Any], challenge_location: str, cutoff: int
) -> None:
    """Calling to get a response"""

    if MOCK_FLAG:
        copy_artifacts_into_workspace(
            config["workspace"], "artifacts_out", challenge_location
        )
    else:
        print(f"Running Python function '{config['entry_path']}' with timeout {cutoff}")
        command = [sys.executable, "-m", config["entry_path"], str(task)]
        test_subprocess = TestSubprocess(command)
        test_subprocess.run(timeout=cutoff)

        if test_subprocess.process and not test_subprocess.process.returncode:
            print("The Python function has finished running.")
        else:
            print("The Python function exited with an error.")


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
