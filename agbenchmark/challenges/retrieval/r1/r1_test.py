from typing import Any, Dict

from agbenchmark.challenges.retrieval.retrieval import RetrievalChallenge


class TestRetrieval(RetrievalChallenge):
    """The first information-retrieval challenge"""

    def test_method(self, config: Dict[str, Any]) -> None:
        self.setup_challenge(config)

        scores = self.get_scores(config)
        assert 1 in scores
