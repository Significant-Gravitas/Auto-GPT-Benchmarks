from lark import Lark


def parse_challenge(challenge_str):
    parser = Lark.open("challenge_lang/challenge.lark")
    return parser.parse(challenge_str)
