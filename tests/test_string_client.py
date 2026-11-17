import pytest
import requests
from services.string_client import StringClient, StringWebAccessError

class Response:
    status_code = 500
    text = '{"error":"bad"}'
    headers = {"Content-Type": "application/json", "X-Request-Id": "req-test"}
    def json(self): return {"error": "bad"}
class Session:
    def post(self, *args, **kwargs): return Response()

def test_api_failure_is_explicit():
    with pytest.raises(StringWebAccessError): StringClient("key", session=Session()).fetch("https://example.com", retries=0)

@pytest.mark.parametrize(("response", "expected"), [
    (type("R", (), {"status_code": 200, "text": '{"data":"hello"}', "headers": {"Content-Type":"application/json"}, "json": lambda self: {"data":"hello"}})(), "hello"),
    (type("R", (), {"status_code": 200, "text": "plain markdown", "headers": {"Content-Type":"text/markdown"}, "json": lambda self: (_ for _ in ()).throw(requests.JSONDecodeError("x", "", 0))})(), "plain markdown"),
])
def test_supported_response_formats(response, expected):
    assert StringClient._parse_response(response, "https://example.com") == expected

def test_plain_text_does_not_attempt_json_parsing():
    response = type("R", (), {"status_code": 200, "text": "# markdown", "headers": {"Content-Type":"text/markdown"}, "json": lambda self: (_ for _ in ()).throw(AssertionError("json() must not be called"))})()
    assert StringClient._parse_response(response, "https://example.com") == "# markdown"

def test_json_without_data_reports_available_keys():
    response = type("R", (), {"status_code": 200, "text": '{"statusCode":200}', "headers": {"Content-Type":"application/json"}, "json": lambda self: {"statusCode":200}})()
    with pytest.raises(StringWebAccessError, match="no data field"):
        StringClient._parse_response(response, "https://example.com")

@pytest.mark.parametrize("response", [
    type("R", (), {"status_code": 200, "text": "", "headers": {"Content-Type":"application/json"}})(),
    type("R", (), {"status_code": 200, "text": "<html>bad gateway</html>", "headers": {"Content-Type":"text/html"}, "json": lambda self: (_ for _ in ()).throw(ValueError())})(),
    type("R", (), {"status_code": 200, "text": "not-json", "headers": {"Content-Type":"application/json"}, "json": lambda self: (_ for _ in ()).throw(ValueError())})(),
])
def test_invalid_responses_raise_descriptive_error(response):
    with pytest.raises(StringWebAccessError): StringClient._parse_response(response, "https://example.com")

def test_execute_js_is_sent_only_when_requested():
    calls = []
    response = type("R", (), {"status_code": 200, "text": "ok", "headers": {"Content-Type":"text/plain"}, "json": lambda self: (_ for _ in ()).throw(ValueError())})()
    session = type("S", (), {"post": lambda self, *args, **kwargs: calls.append(kwargs) or response})()
    StringClient("key", session=session).fetch("https://example.com", retries=0, execute_js=True)
    assert calls[0]["json"] == {"url": "https://example.com", "format": "markdown", "executeJS": True}
    assert calls[0]["headers"]["Authorization"] == "Bearer key"
