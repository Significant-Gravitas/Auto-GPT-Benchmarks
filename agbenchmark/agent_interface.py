import os
import shutil
import subprocess
import sys
import time
from typing import Any, Dict, Optional

from dotenv import load_dotenv

from agbenchmark.start_benchmark import CURRENT_DIRECTORY

load_dotenv()

mock_test_str = os.getenv("MOCK_TEST")
MOCK_FLAG = mock_test_str.lower() == "true" if mock_test_str else False


class TestSubprocess:
    """A convenience class to allow creating a subprocess with a timeout while capturing its output"""

    cmd: list[str]
    process: Optional[subprocess.Popen[str]]

    def __init__(self, cmd: list[str]) -> None:
        self.cmd = cmd
        self.process = None

    def run(self, timeout: int) -> None:
        self.process = subprocess.Popen(
            self.cmd, stdout=sys.stdout, stderr=sys.stderr, universal_newlines=True
        )

        start_time = time.time()
        while self.process.poll() is None:  # None means the process hasn't finished
            if time.time() - start_time > timeout:
                print("The agent timed out")
                self.process.terminate()  # Kill the process
                break

            time.sleep(1)

        if self.process.returncode is not None and self.process.returncode != 0:
            print(f"The agent exited with return code {self.process.returncode}")


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
