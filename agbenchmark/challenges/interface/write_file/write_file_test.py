from typing import Any, Dict

import pytest

from agbenchmark.challenges.interface.interface import InterfaceChallenge


class TestWriteFile(InterfaceChallenge):
    """Testing if LLM can write to a file"""

    @pytest.mark.depends(name="basic_write_file")
    def test_method(self, config: Dict[str, Any]) -> None:
        self.setup_challenge(config)

        files_contents = self.get_artifacts_out(
            config["workspace"], self.data.ground.files
        )

        scores = []
        for file_content in files_contents:
            score = self.scoring(file_content, self.data.ground)
            print("Your score is:", score)
            scores.append(score)

        assert 1 in scores
