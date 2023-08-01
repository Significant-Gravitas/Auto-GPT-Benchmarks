import json
import os
import time
from typing import Optional

import requests

from agbenchmark.start_benchmark import BENCHMARK_START_TIME


def get_data_from_helicone(challenge: str) -> Optional[float]:
    # Define the endpoint of your GraphQL server
    url = "https://www.helicone.ai/api/graphql"

    # Set the headers, usually you'd need to set the content type and possibly an authorization token
    headers = {"authorization": f"Bearer {os.environ.get('HELICONE_API_KEY')}"}

    # Define the query, variables, and operation name
    query = """
query ExampleQuery($properties: [PropertyFilter!]){
  aggregatedHeliconeRequest(properties: $properties) {
    costUSD
  }
}
"""

    variables = {
        "filters": [
            {
                "property": {
                    "value": {"equals": os.environ.get("AGENT_NAME")},
                    "name": "agent",
                }
            },
            {
                "property": {
                    "value": {"equals": BENCHMARK_START_TIME},
                    "name": "benchmark_start_time",
                }
            },
            {"property": {"value": {"equals": challenge}, "name": "challenge"}},
        ]
    }

    operation_name = "ExampleQuery"

    max_retries = 5
    backoff_time = 1  # Start with 1 second

    for retry in range(max_retries):
        try:
            response = requests.post(
                url,
                headers=headers,
                json={
                    "query": query,
                    "variables": variables,
                    "operationName": operation_name,
                },
            )
            response.raise_for_status()

            data = response.json()
            if data and data.get("data"):
                return (
                    data.get("data", {}).get("aggregatedHeliconeRequest", {}).get("costUSD", None)
                )
            else:
                raise ValueError("Invalid response received from server: no data")

        except (requests.HTTPError, json.JSONDecodeError, ValueError) as error:
            print(f"Attempt {retry + 1} failed: {error}")
            if retry < max_retries - 1:  # Don't sleep on the last attempt
                time.sleep(backoff_time)
                backoff_time *= 2  # Exponential backoff
            else:
                print("Max retries reached. Returning 0.")
                return 0

        except Exception as err:
            print(f"Unexpected error occurred on attempt {retry + 1}: {err}")
            raise

    return 0
