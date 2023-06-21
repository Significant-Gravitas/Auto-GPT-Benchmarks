import json
import openai

def basic_gpt_agent(query):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0613", messages=[{"role": "user", "content": query}]
    )

    answer = response["choices"][0]["message"]["content"]  # type: ignore

    output_file = "./workspace/file_to_check.txt"
    with open(output_file, "w") as f:
        f.write(answer)

    print("QUERY       : ", query)
    print("AGENT ANSWER: ", answer)

if __name__ == "__main__":
    # server boilerplate example here
    basic_gpt_agent("")

