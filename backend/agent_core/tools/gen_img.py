# call_via_api_gateway.py
import json
import requests
from typing import Any, Dict

API_URL = "https://71vfitor4i.execute-api.us-east-1.amazonaws.com/dev/generate-image"
REQUEST_TIMEOUT = 120  # seconds - image generation can take time

def invoke_via_api_gateway(use_case: str, user_id: str = "default_user") -> Dict[str, Any]:
    payload = {"use_case": use_case, "user_id": user_id}
    headers = {"Content-Type": "application/json"}

    resp = requests.post(API_URL, headers=headers, json=payload, timeout=REQUEST_TIMEOUT)

    # Raise for 4xx/5xx with helpful body if available
    try:
        resp.raise_for_status()
    except requests.HTTPError:
        # If API Gateway returned a JSON body with error details, include it in the exception
        try:
            err_json = resp.json()
            raise RuntimeError(f"HTTP {resp.status_code}: {err_json}")
        except Exception:
            raise RuntimeError(f"HTTP {resp.status_code}: {resp.text}")

    # Typical API Gateway Lambda proxy integration returns:
    # { "statusCode": 200, "headers": {...}, "body": "<stringified JSON>" }
    try:
        api_wrapper = resp.json()
    except ValueError:
        # Fallback: maybe API returned raw JSON directly
        try:
            return resp.json()
        except Exception:
            raise RuntimeError("Failed to parse API response as JSON")

    body = api_wrapper.get("body", api_wrapper)  # if it's already the body
    # If body is a string (common), parse it
    if isinstance(body, str):
        try:
            body = json.loads(body)
        except json.JSONDecodeError:
            # Body might be a plain string error — return wrapper for debugging
            raise RuntimeError(f"API returned non-JSON body: {body}")

    # At this point body is expected to contain image_urls or error
    if "image_urls" in body:
        return body

    # If there is a generic error shape
    if "error" in body or "error_type" in body:
        raise RuntimeError(f"Invocation returned error: {body}")

    raise RuntimeError(f"Unexpected API response shape: {body}")

if __name__ == "__main__":
    test_use_case = "A mobile app that helps users track their daily water intake and reminds them to stay hydrated."
    try:
        result = invoke_via_api_gateway(test_use_case, user_id="angel27")
        print("Result type:", type(result))
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        print("Error:", e)
