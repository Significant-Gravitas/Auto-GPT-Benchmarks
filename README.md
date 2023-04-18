# Auto-GPT-Benchmarks
A set of standardized benchmarks to assess the performance of Auto-GPTs.

# Overview
The Auto-GPT-Benchmarks project aims to provide a comprehensive suite of benchmarks to evaluate the performance of Auto-GPTs. These benchmarks focus on various tasks, such as code fixes backed by testing, which help to measure the capabilities of the models effectively.

# Key Features
- [ ] Includes a variety of tasks to assess Auto-GPT performance
- [ ] Supports integration with evaluation frameworks for seamless benchmarking
- [ ] Provides token counting and pricing information for models
- [ ] Designed for extensibility to other projects, making it a versatile agent evaluation framework

# Roadmap
## High Priority
1. Develop longer-form tasks, such as code fixes backed by testing, to evaluate the model's performance in more complex scenarios.
2. Identify and address common failure modes in the test harness to improve reliability and stability.
3. Migrate the project to an Ubuntu container to enable better integration with tools like Git and Bash.

### Medium Priority
4. Implement a web server backend for a user-friendly API, replacing the current container and file management approach.
5. Incorporate token counting data from the model and add scores to result files based on token usage and model pricing.

### Low Priority
6. Generalize the framework to support other projects besides Auto-GPT, positioning it as the go-to agent evaluation framework.
7. Preserve OpenAI Eval files from temporary storage to a more permanent location for tracking results.
8. Add support for multi-threaded evaluations to take advantage of OpenAI's capabilities.


## Setup

You must add the auto_gpt_benchmarking dir to the python path
Do this with a path file in your venv. OpenAI evals needs to import it. 

Create a venv with

`python3.9 -m venv venv`

Activate it with

`source venv/bin/activate`

Add a file to `venv/lib/python3.9/site-packages/benchmarking.pth` with the contents: 
`/PATH/TO/REPO/Auto-GPT-Benchmarks-fork`

This is because evals tries to import it directly.

Install the requirements with

`pip install -r requirements.txt`

You must have a docker container built corresponding to the submodule below or the docker run command starting the agent will fail.

Cd into the AutoGPT submodule and build/tag the dockerfile so the agent can be instantiated.
`cd auto_gpt_benchmarks/Auto-GPT`

Build the container so we can run it procedurally! Make sure to have docker running on your computer.
`docker build -t autogpt .`

After docker is built, change directory back to 'Auto-GPT\Auto-GPT-Benchmarks' and set the API Key in command line for windows/mac/linux below

(Windows) 
'set OPENAI_API_KEY=API_key_goes_here'

(Mac/Linux) 
'export OPENAI_API_KEY=API_key_goes_here' 


## Running the tests
In command line after you built the docker file



EVALS_THREADS=1 EVALS_THREAD_TIMEOUT=600 oaieval auto_gpt_completion_fn test-match --registry_path $PWD/auto_gpt_benchmarking

# Understanding OpenAI Evals

The Evals docs are here and very good: https://github.com/openai/evals/tree/main/docs

The basic idea is this:
1. Use a completion function to point to the language model or in our case AutoGPT, the model you want to test.
2. Register that completion function with the evals framework with a yaml in a `completion_fns` dir.
3. Run the evals against the completion function.

Then you can make more yaml defined evals and run them against the completion function as needed.

### Completions Functions

See our yaml file in `completion_fns` dir for the registration of the completion function.
See our completion function itself in CompletionFn.py
That points to the AutoGPT model we want to test which is spun up dynamically in a docker container in AutoGPTAgent.py


# Example final output:

/Auto-GPT-Benchmarks-fork$ cat /tmp/evallogs/230417220821DPM75QNS_auto_gpt_completion_fn_test-match.jsonl
{"spec": {"completion_fns": ["auto_gpt_completion_fn"], "eval_name": "test-match.s1.simple-v0", "base_eval": "test-match", "split": "s1", "run_config": {"completion_fns": ["auto_gpt_completion_fn"], "eval_spec": {"cls": "evals.elsuite.basic.match:Match", "args": {"samples_jsonl": "test_match/samples.jsonl"}, "key": "test-match.s1.simple-v0", "group": "test-basic"}, "seed": 20220722, "max_samples": null, "command": "/home/douglas/AGI/Auto-GPT-Benchmarks-fork/venv/bin/oaieval auto_gpt_completion_fn test-match --registry_path /home/douglas/AGI/Auto-GPT-Benchmarks-fork/auto_gpt_benchmarking", "initial_settings": {"visible": true}}, "created_by": "", "run_id": "230417220821DPM75QNS", "created_at": "2023-04-17 22:08:21.904498"}}
{"final_report": {"accuracy": 0.3333333333333333}}
{"run_id": "230417220821DPM75QNS", "event_id": 0, "sample_id": "test-match.s1.2", "type": "sampling", "data": {"prompt": "Complete the phrase as concisely as possible.\nUser: OpenAI was founded in 20\nAssistant: ", "sampled": "OpenAI was founded in 2015.2015"}, "created_by": "", "created_at": "2023-04-17 22:10:13.127375+00:00"}
{"run_id": "230417220821DPM75QNS", "event_id": 1, "sample_id": "test-match.s1.2", "type": "match", "data": {"correct": false, "expected": "15", "picked": null, "sampled": "OpenAI was founded in 2015.2015", "options": ["15"]}, "created_by": "", "created_at": "2023-04-17 22:10:13.127550+00:00"}
{"run_id": "230417220821DPM75QNS", "event_id": 2, "sample_id": "test-match.s1.1", "type": "sampling", "data": {"prompt": "Complete the phrase as concisely as possible.\nUser: The first US president was \nAssistant: ", "sampled": "George Washington"}, "created_by": "", "created_at": "2023-04-17 22:11:17.761693+00:00"}
{"run_id": "230417220821DPM75QNS", "event_id": 3, "sample_id": "test-match.s1.1", "type": "match", "data": {"correct": true, "expected": "George Washington", "picked": "George Washington", "sampled": "George Washington", "options": ["George Washington"]}, "created_by": "", "created_at": "2023-04-17 22:11:17.761739+00:00"}
{"run_id": "230417220821DPM75QNS", "event_id": 4, "sample_id": "test-match.s1.0", "type": "sampling", "data": {"prompt": "Complete the phrase as concisely as possible.\nUser: Once upon a \nAssistant: ", "sampled": "Once upon a time"}, "created_by": "", "created_at": "2023-04-17 22:12:04.691026+00:00"}
{"run_id": "230417220821DPM75QNS", "event_id": 5, "sample_id": "test-match.s1.0", "type": "match", "data": {"correct": false, "expected": "time", "picked": null, "sampled": "Once upon a time", "options": ["time"]}, "created_by": "", "created_at": "2023-04-17 22:12:04.691064+00:00"}
(venv) douglas@douglas-XPS-15-9500:~/AGI/Auto-GPT-Benchmarks-fork$ 

