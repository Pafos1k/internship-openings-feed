import logging
import time
import json
import requests

log = logging.getLogger(__name__)

class StringWebAccessError(RuntimeError): pass

class StringClient:
    def __init__(self, api_key, endpoint="https://request.usestring.ai/v1/fetch", timeout=30, session=None):
        self.api_key, self.endpoint, self.timeout = api_key, endpoint, timeout
        self.session = session or requests.Session()

    def fetch(self, url, fmt="markdown", retries=2, execute_js=False):
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        payload = {"url": url, "format": fmt}
        if execute_js:
            payload["executeJS"] = True
        for attempt in range(retries + 1):
            try:
                response = self.session.post(self.endpoint, headers=headers, json=payload, timeout=self.timeout)
                return self._parse_response(response, url)
            except (requests.RequestException, StringWebAccessError) as exc:
                if attempt == retries:
                    raise StringWebAccessError(f"String fetch failed for {url}: {exc}") from exc
                time.sleep(2 ** attempt)

    @staticmethod
    def _parse_response(response, url):
        body = response.text or ""
        content_type = response.headers.get("Content-Type", "")
        request_id = next((response.headers.get(name) for name in ("X-Request-Id", "X-Request-ID", "Request-Id", "Cf-Ray") if response.headers.get(name)), "")
        response_metadata = {name: response.headers.get(name) for name in ("x-status-code", "x-final-url", "x-error-code", "retry-after") if response.headers.get(name)}
        preview = body[:500].replace("\r", "\\r").replace("\n", "\\n")
        diagnostic = f"status={response.status_code}, content_type={content_type!r}, body_length={len(body)}, request_id={request_id or 'unavailable'}, metadata={response_metadata}, body_preview={preview!r}"
        log.info("String response for %s: %s", url, diagnostic)

        if not body.strip():
            raise StringWebAccessError(f"String returned an empty response body ({diagnostic})")

        lowered_content_type = content_type.lower()
        if response.status_code >= 400 and "json" not in lowered_content_type:
            raise StringWebAccessError(f"String returned HTTP {response.status_code} as non-JSON content ({diagnostic})")
        if "html" in lowered_content_type or body.lstrip().lower().startswith(("<!doctype html", "<html")):
            raise StringWebAccessError(f"String returned an unexpected HTML page instead of API output ({diagnostic})")
        if lowered_content_type.startswith("text/") and "json" not in lowered_content_type:
            return body

        looks_like_json = body.lstrip().startswith(("{", "["))
        if "json" not in lowered_content_type and not looks_like_json:
            raise StringWebAccessError(f"String returned an unsupported non-JSON response format ({diagnostic})")

        try:
            parsed = response.json()
        except (requests.JSONDecodeError, json.JSONDecodeError, ValueError) as exc:
            raise StringWebAccessError(f"String returned invalid JSON ({diagnostic})") from exc

        if parsed is not None:
            if not isinstance(parsed, dict):
                raise StringWebAccessError(f"String returned an unexpected JSON value ({diagnostic})")
            if parsed.get("error"):
                metadata = {key: parsed.get(key) for key in ("error", "message", "code", "reason", "requestId") if parsed.get(key) is not None}
                raise StringWebAccessError(f"String returned an API error: {metadata} ({diagnostic})")
            if "data" not in parsed:
                raise StringWebAccessError(f"String JSON response has no data field; keys={sorted(parsed)} ({diagnostic})")
            data = parsed["data"]
            if not isinstance(data, str) or not data.strip():
                raise StringWebAccessError(f"String JSON data field is empty or not text ({diagnostic})")
            if response.status_code >= 400:
                raise StringWebAccessError(f"String returned HTTP {response.status_code} with data ({diagnostic})")
            return data
