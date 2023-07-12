from mitmproxy import http


def request(flow: http.HTTPFlow) -> None:
    print(f"Request: {flow.request.pretty_url}")
    print(f"Request Headers: {flow.request.headers}")
    print(f"Request Body: {flow.request.get_text()}")


def response(flow: http.HTTPFlow) -> None:
    if flow.response:
        print(f"Response: {flow.response}")
        print(f"Response Headers: {flow.response.headers}")
        print(f"Response Body: {flow.response.get_text()}")
