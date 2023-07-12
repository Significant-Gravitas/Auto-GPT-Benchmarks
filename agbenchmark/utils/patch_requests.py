import builtins
import requests as requests_actual


def logging_post(*args, **kwargs):
    print(f"Sending request: POST {args[0]}")
    print(f"Request headers: {kwargs.get('headers')}")
    print(f"Request body: {kwargs.get('data')}")
    response = requests_actual.post(*args, **kwargs)
    print(f"Received response: {response.status_code} {response.reason}")
    print(f"Response headers: {response.headers}")
    print(f"Response body: {response.text}")
    return response


# Replace the original post method with our logging version
requests_actual.post = logging_post

# Export requests_actual under the name requests
builtins.requests = requests_actual  # type: ignore
