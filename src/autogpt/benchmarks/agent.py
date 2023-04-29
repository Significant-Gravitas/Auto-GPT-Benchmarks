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

from aiodocker.containers import DockerContainer

from . import constants


class DockerContainerConfiguration:
    @classmethod
    def from_agent(cls, agent: "AutoGPTAgent", **extras):
        return cls(agent.auto_gpt_path, **extras)

    def __init__(self, root: Path, **extras):
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
        lines = filter(lambda line: line[0] != "#", lines)
        # Run the generator pipeline
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
            "environment": self.get_environment_variables(),
            "volumes": self.get_volumes(),
        }


class DockerContainerLogListener:
    def __init__(self, container: DockerContainer, **configs):
        self.container = container
        self.configs = dict(configs)

    async def run(self):
        try:
            async for line in self.container.log(**self.config):
                logging.info(line.strip())
                await asyncio.sleep(1)

        except aiodocker.exceptions.DockerError:
            logging.exception("Container killed or removed.")


class AutoGPTWorkspace:
    def __init__(self, root: Path):
        self.root = root
        self.prompt = self.root / "prompt.txt"
        self.output = self.root / "output.txt"
        self.ai_settings = self.root / "ai_settings.yaml"


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

    container: DockerContainer
    listener: asyncio.Task
    killing: bool = False

    def __init__(self, prompt: str, path: str):
        self.prompt = prompt
        self.root = Path(path)
        self.workspace = AutoGPTWorkspace(self.root / "auto_gpt_workspace")

    async def setup(self):
        # if the workspace doesn't exist, create it
        if not self.auto_workspace.root.exists():
            self.auto_workspace.root.mkdir()

        await self.cleanup()
        self.workspace.ai_settings.write_text(constants.AI_SETTINGS.read_text())
        self.worspace.prompt.write_text(self.prompt)

    async def cleanup(self):
        """
        Cleans up the workspace by deleting the prompt.txt and output.txt files.
        Check if the files are there and delete them if they are
        """
        # fmt:off
        if self.prompt_file.exists(): self.prompt_file.unlink()
        if self.output_file.exists(): self.output_file.unlink()
        if self.file_logger.exists(): self.file_logger.unlink()
        # fmt:on

    async def start(self):
        """
        Run the agent in a docker container, assuming you have:

            1. Build the docker image built with:

                > docker build -t autogpt .

            2. Set up the .env file in the Auto-GPT repo.

        Awaits an answer
        """
        # Set up the agent by cleaning the workspace and copying the settings
        await self.setup()

        # Create a container that runs the autogpt image continuously
        async with docker.from_env() as client:
            self.container = client.containers.run(
                image="autogpt",
                command="--continuous -C '/app/config/ai_settings.yaml'",
                **self.get_container_configuration().dict(),
            )

        # Hook up a continuous log listener attached to the container
        self.listener = asyncio.create_task(
            DockerContainerLogListener(
                self.container, stdout=True, stderr=True, follow=True, tail="all"
            )
        )

        # Poll continuously for an answer
        answer = await self.wait_for_answer()

        logging.info(f"Prompt: {self.prompt}, Answer: {answer}")
        await self.kill()

        return answer

    def get_container_configuration(self) -> DockerContainerConfiguration:
        return DockerContainerConfiguration(
            self.auto_gpt_path,
            stdin_open=True,
            tty=True,
            detach=True,
        )

    async def wait_for_answer(self):
        """Polls until output.txt exists, and return its contents."""
        while True:
            if self.output_file.exists():
                return self.output_file.read_text()

    async def kill(self):
        # fmt:off
        if self.killing: return
        self.killing = True

        # Clean-up the workspace
        self.cleanup()

        # Kill and remove the container if we have one
        if self.container:
            try:
                self.container.kill()
                self.container.remove()

            except docker.errors.APIError:
                logging.exception(
                    f"Couldn't find container:{repr(self.container)} to kill. "
                    "Assuming container successfully killed itself."
                )

        # Assuming that the listener exists and it's errored out and returned
        # on Container Not Found
        if self.listener and self.listener.done():
            self.listener = None

        # DONE
        self.killing = False
        # fmt:on
