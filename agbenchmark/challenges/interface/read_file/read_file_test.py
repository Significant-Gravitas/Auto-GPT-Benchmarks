from typing import Any, Dict

from agbenchmark.challenges.interface.interface import InterfaceChallenge


class TestReadFile(InterfaceChallenge):
    """Testing if LLM can read a file"""

    def test_method(self, config: Dict[str, Any]) -> None:
        self.setup_challenge(config)
        scores = self.get_scores(config)
        assert 1 in scores
