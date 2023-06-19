def execute_challenge(challenge, ai_agent):
    print(f"Description: {challenge['description']}")
    print("Artifacts:")
    for artifact in challenge["artifacts"]:
        print(artifact)
    print("Tasks:")
    for task in challenge["tasks"]:
        print(task)
    print("Success Criteria:")
    for criteria in challenge["success_criteria"]:
        print(criteria)

    # TODO: Implement the logic to actually execute the challenge with Any AI agent
