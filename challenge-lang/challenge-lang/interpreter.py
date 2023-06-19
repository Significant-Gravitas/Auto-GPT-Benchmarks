from lark import Transformer

from .parser import parse_challenge


class ChallengeTransformer(Transformer):
    def challenge(self, items):
        return {
            "description": items[0],
            "artifacts": items[1],
            "tasks": items[2],
            "success_criteria": items[3],
        }

    def description(self, items):
        return str(items[0])

    def artifacts(self, items):
        return [str(item) for item in items]

    def tasks(self, items):
        return [str(item) for item in items]

    def success_criteria(self, items):
        return [str(item) for item in items]


def interpret_challenge(challenge_str, transformer=ChallengeTransformer()):
    tree = parse_challenge(challenge_str)
    transformed_challenge = transformer.transform(tree)
    return transformed_challenge
