from typing import Any, Dict

from agbenchmark.challenges.memory.memory import MemoryChallenge


class TestRememberMultipleIds(MemoryChallenge):
    """The first memory challenge"""

    def test_method(self, config: Dict[str, Any]) -> None:
        self.setup_challenge(config)

        scores = self.get_scores(config)
        assert 1 in scores
