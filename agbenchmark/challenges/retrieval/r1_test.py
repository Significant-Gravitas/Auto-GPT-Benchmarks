import pytest
from Retrieval import RetrievalChallenge
from agbenchmark.challenges.define_task_types import Challenge, Ground

data = Challenge(
    category="retrieval",
    task="What is the capital of America?",
    ground=Ground(
        answer="Washington",
        should_contain=["Washington"],
        should_not_contain=["New York", "Los Angeles", "San Francisco"],
        files=["file_to_check.txt"],
    ),
    difficulty="easy",
)


class TestRetrieval1(RetrievalChallenge):
    """The first information-retrieval challenge"""

    @pytest.mark.parametrize(
        "server_response",
        [data.task],
        indirect=True,
    )
    @pytest.mark.retrieval
    def test_retrieval(self, workspace):
        file = self.open_file(workspace, data.ground.files[0])

        score = self.scoring(file, data.ground)

        print("You score is:", score)

        assert score
