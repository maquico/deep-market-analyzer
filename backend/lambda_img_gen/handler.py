import base64
import json
import os
import random
from string import Template
import boto3

# Constants
IMAGE_MODEL_ID = "amazon.nova-canvas-v1:0"
TEXT_MODEL_ID = "amazon.nova-pro-v1:0"
BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
REGION_NAME = os.getenv("AWS_REGION")

# Create AWS clients outside the handler (best practice for Lambda)
client = boto3.client("bedrock-runtime", region_name=REGION_NAME)
s3_client = boto3.client('s3', region_name=REGION_NAME)



### Setting Prompts ###
SYSTEM_PROMPT_GENERATING_PRODUCT_DESCRIPTION = """
You are **Image Prompt Composer**.

1. **Analyze** the user’s product idea and the **use case** to understand the **final product** (physical or software artifact and its visible UI/hardware).
2. **Synthesize** a single concise **caption-style** image prompt that visually represents the product doing its job in context.
3. **Output exactly two fields** as strict JSON:

```json
{"prompt":"...", "negativeText":"..."}
```

**Rules for `prompt` (follow strictly):**

* Write like an **image caption**, not commands; **do not use negations** here. Include **subject**, **environment**, **composition/framing**, **materials/textures**, **lighting**, **mood**, and (if relevant) **style/camera/angle/UI elements**. Keep under **600 characters**. ([AWS Documentation][2])
  **Rules for `negativeText`:**
* Put all exclusions here (e.g., quality defects, brand/text artifacts, anatomy issues, unwanted styles). Keep concise. ([AWS Documentation][3])
  **Structured output requirement:** Return only the JSON with those two keys and nothing else. ([AWS Documentation][4])

**Few-shot exemplars (pattern to imitate):** ([AWS Documentation][5])
Example 1 — Retail shelf-scanner handheld
**Input (use-case):** “Rugged handheld to speed shelf audits; barcode scan, offline ERP sync.”
**Output JSON:**

```json
{
  "prompt": "rugged handheld barcode device on a grocery aisle endcap, matte polymer body with sealed ports and textured grips, 5-inch screen showing inventory variance tiles, warm store lighting, shallow depth of field, three-quarter product angle, clean background with blurred shelves",
  "negativeText": "blurry, low-res, watermark, brand logos, text artifacts on UI, warped geometry, overexposed highlights, heavy noise"
}
```

Example 2 — B2B analytics dashboard (software UI)
**Input (use-case):** “Web app that forecasts supply risk; scenario sliders; geospatial map.”
**Output JSON:**

```json
{
  "prompt": "ultra-clean web dashboard on a wide monitor, dark top nav, left filters, center geospatial heatmap with risk choropleth, right panel with scenario sliders and probability sparklines, soft ambient office light, slight screen glow, front-oblique angle",
  "negativeText": "illegible UI text, fake vendor logos, oversaturation, low contrast, blur, heavy gradients, cartoonish style"
}
```

Example 3 — Smart water bottle for athletes
**Input (use-case):** “Tracks hydration, temperature; haptic reminder; app pairing.”
**Output JSON:**

```json
{
  "prompt": "sleek stainless smart water bottle on a gym bench, subtle LED ring near cap, condensation beads on brushed metal, phone beside it showing hydration rings, morning window light, shallow depth, three-quarter product render",
  "negativeText": "brand labels, text artifacts, extra buttons, distorted reflections, bad anatomy, harsh glare, jpeg artifacts"
}
```
"""

USER_PROMPT_GENERATING_PRODUCT_DESCRIPTION = Template("""
From the following **company use-case description(s)**, produce the two-field JSON. First analyze the product and use-case to infer the final product; then compose the caption and the negative prompt.

## Output (return exactly this JSON, nothing else)

```json
{
  "prompt": "string (≤600 chars; caption-style; include subject, environment, composition, materials/textures, lighting, mood, optional style/camera/UI; no negations)",
  "negativeText": "string (concise exclusions: defects, artifacts, unwanted styles/objects/branding/anatomy issues)"
}
```
## Input
```
$use_case
```
""")

def generate_image_prompt(use_case: str) -> dict:
    """
    Generate an image prompt and negative text using the text model.
    """
    user_full_prompt = USER_PROMPT_GENERATING_PRODUCT_DESCRIPTION.substitute(use_case=use_case)
    
    response = client.converse(
        modelId=TEXT_MODEL_ID,
        system=[
            {
                'text': SYSTEM_PROMPT_GENERATING_PRODUCT_DESCRIPTION,
            }
        ],
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "text": user_full_prompt,
                    }
                ]
            }
        ]
)
    
    response_text = response["output"]["message"]["content"][0]["text"]
    
    try:
        prompt_data = json.loads(response_text.replace("```json", "").replace("```", "").strip())
        return prompt_data
    except json.JSONDecodeError:
        raise ValueError("Failed to parse JSON from model response")


def generate_image(use_case: str, user_id: str = "default_user") -> list[str]:
    seed = random.randint(0, 858993460)
    # Generate the image prompt
    prompt_data = generate_image_prompt(use_case)
    # Format the request payload using the model's native structure.
    native_request = {
        "taskType": "TEXT_IMAGE",
        "textToImageParams": {
            "text": prompt_data["prompt"], 
            "negativeText": prompt_data["negativeText"]
        },
        "imageGenerationConfig": {
            "seed": seed,
            "quality": "standard",
            "height": 1024,
            "width": 1024,
            "numberOfImages": 3
        },
    }

    # Convert the native request to JSON.
    request = json.dumps(native_request)

    # Invoke the model with the request.
    response = client.invoke_model(modelId=IMAGE_MODEL_ID, body=request)

    # Decode the response body.
    model_response = json.loads(response["body"].read())
    
    images_paths = []
    for idx, base64_image_data in enumerate(model_response["images"]):
        image_data = base64.b64decode(base64_image_data)
        image_name = f"generated_image_{seed}_{idx+1}.png"
        image_path = f"{user_id}/{image_name}"
        
        # Save image to S3
        save_image_s3(image_data, image_name, user_id)
        
        # Generate presigned URL valid for 1 hour (3600 seconds)
        presigned_url = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': BUCKET_NAME,
                'Key': image_path
            },
            ExpiresIn=3600  # 1 hour
        )
        
        images_paths.append(presigned_url)
    
    return images_paths

def save_image_s3(images_bytes: str, image_name: str, user_id: str) -> None:
    """
    Save image to S3 bucket.
    """
    image_path = f"{user_id}/{image_name}"
    s3_client.put_object(Bucket=BUCKET_NAME, Key=image_path, Body=images_bytes, ContentType='image/png')


def lambda_handler(event, context):
    """
    AWS Lambda handler function.
    Accepts events from API Gateway or direct Lambda invocation.
    
    Expected input formats:
    - API Gateway: {"body": "{\"use_case\": \"...\", \"user_id\": \"...\"}"}
    - Direct invocation: {"use_case": "...", "user_id": "..."}
    
    Returns:
    - API Gateway format: {"statusCode": 200, "body": "{\"image_urls\": [...]}"}
    - Direct invocation format: {"image_urls": [...]}
    """
    try:
        # Determine if the event is from API Gateway or direct invocation
        print("Decoding event:", event)
        if 'body' in event:
            raw = event["body"] or ""
            if event.get("isBase64Encoded"):
                raw = base64.b64decode(raw).decode("utf-8", errors="replace")
            body = json.loads(raw) if isinstance(raw, str) else raw
        
        print("Extracting parameters")
        # Extract parameters
        use_case = body.get('use_case')
        user_id = body.get('user_id', 'default_user')
        
        print(f"Use case: {use_case}, User ID: {user_id}")
        # Validate use_case
        if not use_case:
            error_response = {
                "error": "Missing required parameter: use_case"
            }
            if 'body' in event:
                return {
                    "statusCode": 400,
                    "headers": {
                        "Content-Type": "application/json",
                        "Access-Control-Allow-Origin": "*"
                    },
                    "body": json.dumps(error_response)
                }
            else:
                return error_response
        
        # Generate images
        image_urls = generate_image(use_case, user_id)
        
        # Prepare success response
        success_response = {
            "image_urls": image_urls,
            "use_case": use_case,
            "user_id": user_id,
            "count": len(image_urls)
        }
        
        # Return response based on invocation type
        if 'body' in event:
            # API Gateway response
            return {
                "statusCode": 200,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*"
                },
                "body": json.dumps(success_response)
            }
        else:
            # Direct invocation response
            return success_response
            
    except Exception as e:
        error_response = {
            "error": str(e),
            "error_type": type(e).__name__
        }
        
        if 'body' in event:
            return {
                "statusCode": 500,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*"
                },
                "body": json.dumps(error_response)
            }
        else:
            return error_response


if __name__ == "__main__":
    test_use_case = "A mobile app that helps users track their daily water intake and reminds them to stay hydrated."
    print(generate_image(test_use_case))