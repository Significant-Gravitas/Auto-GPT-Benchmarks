"""
This instantiates an AutoGPT agent who is capable of handling any task.
It is designed to pass benchmarks as effectively as possible.

Loads in the ai_settings.yaml file to get the AI's name, role, and goals.
Sets the ai to continuous mode, but kills it if it takes more than 50,000
tokens on any particular evaluation.

The model is instantiated with a prompt from the AutoGPT completion function.

Eventualy we will also save and log all of the associated output and thinking
for the model as well.
"""
import logging
from pathlib import Path

import asyncio
import aiodocker
import docker


class ContainerConfiguration:
    def __init__(self, image: str, root: Path, **extras):
        self.image = image
        self.root = root
        self.workspace = root / "auto_gpt_workspace"
        self.extras = dict(extras)

    def get_environment_variables(self):
        with open(self.root / ".env", "r") as envfile:
            # Read the lines from the .env file
            lines = (line.strip() for line in envfile.readlines())

        # Remove any blank lines
        lines = filter(bool, lines)
        # Remove any connected out lines
        lines = filter(lambda l: l[0] != "#", lines)

        return list(lines)

    def get_volumes(self):
        return {
            str(self.workspace): {
                "bind": "/home/appuser/auto_gpt_workspace",
                "mode": "rw",
            },
            str(self.root / "autogpt"): {
                "bind": "/home/appuser/autogpt",
                "mode": "rw",
            },
        }

    def dict(self):
        return {
            "image": self.image,
            "environment": self.get_environment_variables(),
            "volumes": self.get_volumes(),
        }


class AutoGPTAgent:
    """
    A class object that contains the configuration information for the AI.
    The __init__ function takes an evaluation prompt.

    Steps:
        * Copy the ai_settings.yaml file in AutoGPTData to the Auto-GPT repo.
        * Copy the prompt to ./Auto-GPT/auto_gpt_workspace/prompt.txt.
        * Polls for token usage and for ./Auto-GPT/auto_gpt_workspace/output.txt.
        * Kills models using more than 50,000 tokens.
        * Otherwise, returns the output.txt file.
    """

    def __init__(self, prompt, auto_gpt_path: str):
        self.auto_gpt_path = Path(auto_gpt_path)
        self.auto_workspace = self.auto_gpt_path / "auto_gpt_workspace"

        # if the workspace doesn't exist, create it
        if not self.auto_workspace.exists():
            self.auto_workspace.mkdir()

        self.prompt_file = self.auto_workspace / "prompt.txt"
        self.output_file = self.auto_workspace / "output.txt"
        self.file_logger = self.auto_workspace / "file_logger.txt"
        self.ai_settings_file = (
            Path(__file__).parent / "AutoGPTData" / "ai_settings.yaml"
        )
        self.ai_settings_dest = self.auto_workspace / "ai_settings.yaml"
        self.prompt = prompt
        self._clean_up_workspace()
        self._copy_ai_settings()
        self._copy_prompt()
        self.container = None
        self.killing = False
        self.logging_task = None

    def _clean_up_workspace(self):
        """
        Cleans up the workspace by deleting the prompt.txt and output.txt files.
        Check if the files are there and delete them if they are
        """ 
        # fmt:off
        if self.prompt_file.exists(): self.prompt_file.unlink()
        if self.output_file.exists(): self.output_file.unlink()
        if self.file_logger.exists(): self.file_logger.unlink()
        # fmt:on

    def _copy_ai_settings(self):
        self.ai_settings_dest.write_text(self.ai_settings_file.read_text())

    def _copy_prompt(self):
        self.prompt_file.write_text(self.prompt)

    async def _stream_logs(self, container: aiodocker.containers.DockerContainer):
        try:
            async for line in container.log(
                stdout=True, stderr=True, follow=True, tail="all"
            ):
                logging.info(line.strip())
                await asyncio.sleep(1)

        except aiodocker.exceptions.DockerError:
            logging.exception("Container killed or removed.")

    async def _run_stream_logs(self):
        """
        This grabs the docker containers id and streams the logs to the console
        with aiodocker.
        """
        async with aiodocker.Docker() as docker_client:
            try:
                container = docker_client.containers.container(self.container.id)
                await self._stream_logs(container)

            except aiodocker.exceptions.DockerError:
                logging.exception("Container not found.")

    def get_container_configuration(self) -> ContainerConfiguration:
        extras = {"stdin_open": True, "tty": True, "detach": True}
        return ContainerConfiguration("autogpt", self.auto_gpt_path, **extras)

    def _start_agent(self):
        """
        Starts the agent in a docker container, assuming you have:
        
            1. Build the docker image built with:

                > docker build -t autogpt .

            2. Set up the .env file in the Auto-GPT repo.

        """
        client = docker.from_env()
        self.container = client.containers.run(
            command="--continuous -C '/home/appuser/auto_gpt_workspace/ai_settings.yaml'",
            **self.get_container_configuration().dict()
        )
        asyncio.run(self._run_stream_logs())

    def _poll_for_output(self):
        """
        This polls the output file to see if the model has finished.
        :return:
        """
        while True:
            if self.output_file.exists():
                return self.output_file.read_text()

    def start(self):
        self._start_agent()
        answer = self._poll_for_output()
        logging.info(f"Prompt: {self.prompt}, Answer: {answer}")
        self.kill()
        return answer

    def kill(self):
        # fmt:off
        if self.killing: return
        self.killing = True
        self._clean_up_workspace()

        if self.container:
            try:
                self.container.kill()
                self.container.remove()

            except docker.errors.APIError:
                logging.exception(
                    f"Couldn't find container:{repr(self.container)} to kill. "
                    "Assuming container successfully killed itself."
                )

            if self.logging_task: self.logging_task.cancel()

        self.killing = False
        # fmt:on
