# call_via_api_gateway.py
import json
import requests
from typing import Any, Dict
import uuid
from dynamo_handler import add_image_record

API_URL = "https://71vfitor4i.execute-api.us-east-1.amazonaws.com/dev/generate-image"
REQUEST_TIMEOUT = 120  # seconds - image generation can take time
DYNAMO_TABLE_NAME = "deep-market-analyzer-images"

def invoke_via_api_gateway(use_case: str, chat_id: str, user_id: str = "default_user", ) -> Dict[str, Any]:
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
        saved_images = []
        for image_url in body["image_urls"]:
            image_obj = {}
            image_obj["image_id"] = str(uuid.uuid4())
            image_obj["chat_id"] = chat_id
            image_obj["user_id"] = user_id
            image_obj["description"] = use_case
            image_obj["s3_bucket"] = image_url.split("//")[1].split(".")[0]  # Extract bucket
            image_obj["s3_key"] = image_url.split("//")[1].split("/", 1)[1].split("?")[0]  # Extract key  # Extract key
            add_image_record(image_obj)
            image_obj["presigned_url"] = image_url
            saved_images.append(image_obj)
            
        # Return ids, desc, and original presigned urls
        final_body = {
            "images": [
                {
                    "image_id": img["image_id"],
                    "description": img["description"],
                    "presigned_url": img["presigned_url"]
                } for img in saved_images
            ]
        }
        return final_body

    # If there is a generic error shape
    if "error" in body or "error_type" in body:
        raise RuntimeError(f"Invocation returned error: {body}")

    raise RuntimeError(f"Unexpected API response shape: {body}")

if __name__ == "__main__":
    test_use_case = "A mobile app that helps users track their daily water intake and reminds them to stay hydrated."

    try:
        result = invoke_via_api_gateway(test_use_case, chat_id="2853a8e2-2702-4cc4-a022-e1dcb7b813c3",user_id="angel27")
        print("Result type:", type(result))
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        print("Error:", e)
