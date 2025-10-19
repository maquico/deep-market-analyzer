# Lambda Image Generator Service

AWS Lambda service that generates product concept images using Amazon Bedrock Nova Canvas based on business use case descriptions, with automatic S3 storage.

## 📋 Features

- **🎨 AI Image Generation**: Creates images using **Amazon Bedrock Nova Canvas**
- **🧠 Smart Analysis**: Use case analysis with **Amazon Nova Pro**
- **✨ Auto-Optimization**: Automatically generates optimized prompts
- **🔢 Multiple Variations**: Generates 3 image variations per request
- **☁️ S3 Integration**: Automatic upload to S3
- **🔗 Presigned URLs**: Valid for 1 hour
- **📁 Organization**: User-based folder structure in S3
- **🚀 Flexible Invocation**: API Gateway and direct Lambda support
- **📐 High Quality**: 1024x1024 px images

## 🚀 Project Structure

```
.
├── handler.py           # Main Lambda function with image generation logic
├── serverless.yml       # Serverless Framework configuration
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## 📦 Prerequisites

1. **AWS CLI** configured with credentials
2. **Serverless Framework** installed:
   ```bash
   npm install -g serverless
   ```
3. **Python 3.12** installed
4. **Amazon Bedrock** access to Nova models
5. **S3 Bucket** for image storage

## 🔧 Configuration

### 1. Setup the project

```bash
# Install Serverless Framework (if not installed)
npm install -g serverless

# Install Python dependencies (optional for local development)
pip install -r requirements.txt
```

### 2. Configure environment variables

Create a `.env` file in the project root:

```env
S3_BUCKET_NAME=your-bucket-name
AWS_REGION=us-east-1
```

### 3. Configure AWS Credentials

```bash
serverless config credentials --provider aws --key YOUR_ACCESS_KEY --secret YOUR_SECRET_KEY
```

## 🚢 Deployment

### Deploy to AWS

```bash
# Deploy to staging (dev)
serverless deploy

# Deploy to production
serverless deploy --stage prod

# Deploy to specific region
serverless deploy --region us-east-1
```

After deployment, you'll get an endpoint like:
```
POST - https://xxxxxxxxxx.execute-api.us-east-1.amazonaws.com/dev/generate-image
```

### View logs

```bash
serverless logs -f generateImage --tail
```

### Remove the service

```bash
serverless remove
```

## 📡 API Usage

### Endpoint

```
POST https://your-api-gateway-url/generate-image
```

### Request Payload

```json
{
  "use_case": "A mobile app that helps users track their daily water intake and reminds them to stay hydrated.",
  "user_id": "user123",  // Optional - default: "default_user"
  "chat_id": "chat456"   // Optional - for context tracking
}
```

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `use_case` | string | ✅ Yes | - | Business use case or product description |
| `user_id` | string | No | `"default_user"` | User folder in S3 |
| `chat_id` | string | No | null | Chat/session identifier |

### Successful Response

```json
{
  "images": [
    {
      "image_id": "img_1234567890_1",
      "presigned_url": "https://bucket.s3.us-east-1.amazonaws.com/user123/img_1234567890_1.png?X-Amz-Algorithm=...",
      "description": "Sleek mobile app interface showing water intake tracker with blue gradient and hydration reminders"
    },
    {
      "image_id": "img_1234567890_2",
      "presigned_url": "https://bucket.s3.us-east-1.amazonaws.com/user123/img_1234567890_2.png?X-Amz-Algorithm=...",
      "description": "Mobile app dashboard with water bottle visualization and daily hydration progress rings"
    },
    {
      "image_id": "img_1234567890_3",
      "presigned_url": "https://bucket.s3.us-east-1.amazonaws.com/user123/img_1234567890_3.png?X-Amz-Algorithm=...",
      "description": "Water tracking app notification screen with reminder to drink water and hydration statistics"
    }
  ],
  "use_case": "A mobile app that helps users track their daily water intake...",
  "user_id": "user123",
  "count": 3
}
```

### Error Response

```json
{
  "error": "Missing required parameter: use_case",
  "error_type": "ValueError"
}
```

---

## 📂 S3 Storage Structure

```
s3://your-bucket/
└── {user_id}/
    ├── img_{timestamp}_1.png
    ├── img_{timestamp}_2.png
    └── img_{timestamp}_3.png
```

Example:
```
s3://my-bucket/
└── user123/
    ├── img_1234567890_1.png
    ├── img_1234567890_2.png
    └── img_1234567890_3.png
```

---

## 🎨 Examples

### Example 1: Physical Product

```bash
curl -X POST https://your-api-endpoint/dev/generate-image \
  -H "Content-Type: application/json" \
  -d '{
    "use_case": "Rugged handheld device for retail shelf audits with barcode scanning and offline ERP sync capabilities.",
    "user_id": "retail_team"
  }'
```

### Example 2: Software Dashboard

```bash
curl -X POST https://your-api-endpoint/dev/generate-image \
  -H "Content-Type: application/json" \
  -d '{
    "use_case": "Web application that forecasts supply chain risks with interactive scenario sliders and geospatial risk map visualization.",
    "user_id": "analytics_team"
  }'
```

### Example 3: IoT Device

```bash
curl -X POST https://your-api-endpoint/dev/generate-image \
  -H "Content-Type: application/json" \
  -d '{
    "use_case": "Smart water bottle for athletes that tracks hydration levels, temperature, sends haptic reminders, and pairs with mobile app.",
    "user_id": "fitness_team"
  }'
```

### Example 4: Direct Lambda Invocation (No API Gateway)

```python
import boto3
import json

lambda_client = boto3.client('lambda', region_name='us-east-1')

response = lambda_client.invoke(
    FunctionName='aws-lambda-image-generation-dev-generateImage',
    InvocationType='RequestResponse',
    Payload=json.dumps({
        'use_case': 'A mobile fitness tracking app',
        'user_id': 'test_user'
    })
)

result = json.loads(response['Payload'].read())
print(result['images'])
```

---

## 🧪 Local Testing

```bash
# Activate virtual environment
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Run local test
python handler.py
```

---

## 💡 Use Cases

### Product Visualization
- Generate concept images for physical products
- Visualize hardware prototypes
- Create product mockups for presentations

### Software UI/UX
- Dashboard and interface concepts
- Mobile app screen designs
- Web application layouts

### IoT & Smart Devices
- Smart device concepts
- Wearable technology designs
- Connected product visualizations

### Marketing & Pitches
- Investor presentation visuals
- Product pitch materials
- Marketing campaign concepts

---

## 🤖 AI Models Used

### Amazon Bedrock Nova Pro (Text)
- **Model ID**: `amazon.nova-pro-v1:0`
- **Purpose**: Use case analysis and optimized prompt generation
- **Features**: 
  - Advanced business context understanding
  - Structured prompt generation
  - JSON output format

### Amazon Bedrock Nova Canvas (Images)
- **Model ID**: `amazon.nova-canvas-v1:0`
- **Purpose**: Product image generation
- **Specifications**:
  - Resolution: 1024x1024 px
  - Quality: Standard
  - Format: PNG
  - Quantity: 3 images per request

---

## ⚙️ Technical Details

### Lambda Configuration
- **Memory**: 1024 MB
- **Timeout**: 300 seconds (5 minutes)
- **Runtime**: Python 3.12
- **Architecture**: x86_64

### API Gateway
- **CORS**: Enabled for all origins (`*`)
- **Binary Media Types**: `image/png`, `image/jpeg`, `application/json`
- **Methods**: POST, OPTIONS

### Dependencies
```txt
boto3>=1.34.0
botocore>=1.34.0
python-dotenv>=1.0.0
```

**Note**: `boto3` and `botocore` are already included in AWS Lambda environment.

### IAM Permissions Required

#### Amazon Bedrock
```json
{
  "Effect": "Allow",
  "Action": [
    "bedrock:InvokeModel",
    "bedrock:InvokeModelWithResponseStream",
    "bedrock:Converse",
    "bedrock:ConverseStream"
  ],
  "Resource": [
    "arn:aws:bedrock:us-east-1::foundation-model/amazon.nova-canvas-v1:0",
    "arn:aws:bedrock:us-east-1::foundation-model/amazon.nova-pro-v1:0"
  ]
}
```

#### Amazon S3
```json
{
  "Effect": "Allow",
  "Action": [
    "s3:PutObject",
    "s3:PutObjectAcl",
    "s3:GetObject",
    "s3:ListBucket"
  ],
  "Resource": [
    "arn:aws:s3:::your-bucket-name",
    "arn:aws:s3:::your-bucket-name/*"
  ]
}
```

---

## 🎯 Prompt Engineering

The function uses an advanced prompt engineering system with:

1. **Few-shot Learning**: Examples of physical products, dashboards, and IoT devices
2. **Structured Output**: Prompts and negatives in JSON format
3. **Caption-Style Prompts**: Natural descriptions instead of commands
4. **Negative Prompts**: Exclusion of quality defects, artifacts, and unwanted styles

### Anatomy of a Generated Prompt

```json
{
  "prompt": "sleek stainless smart water bottle on a gym bench, subtle LED ring near cap, condensation beads on brushed metal, phone beside it showing hydration rings, morning window light, shallow depth, three-quarter product render",
  "negativeText": "brand labels, text artifacts, extra buttons, distorted reflections, bad anatomy, harsh glare, jpeg artifacts"
}
```

---

## 🔒 Security

- ✅ Presigned URLs with 1-hour expiration
- ✅ No public S3 bucket required
- ✅ Temporary access without credentials
- ✅ CORS configured for security
- ✅ Input parameter validation

---

## 🚨 Limitations and Considerations

1. **Presigned URLs**: Expire after 1 hour
2. **Timeout**: Generation can take up to 2-3 minutes per request
3. **Costs**: 
   - Amazon Bedrock charges per token (text) and generated images
   - S3 charges for storage and transfer
4. **Bedrock Limits**: Check AWS service quotas
5. **Region**: Nova models must be available in selected region (us-east-1 recommended)

---

## 📊 Monitoring

### View Real-time Logs

```bash
serverless logs -f generateImage --tail
```

### CloudWatch Metrics
- Invocations
- Duration
- Errors
- Throttles

---

## 🔄 Useful Commands

```bash
# View deployment information
serverless info

# Invoke function directly
serverless invoke -f generateImage --data '{"use_case":"test product","user_id":"test"}'

# View logs
serverless logs -f generateImage

# Remove deployment
serverless remove
```

---

## 🐛 Troubleshooting

### Error: "Missing required parameter: use_case"
- **Cause**: Payload doesn't include `use_case` field
- **Solution**: Ensure required field is sent in body

### Error: "Failed to parse JSON from model response"
- **Cause**: Nova Pro didn't return valid JSON
- **Solution**: Review system prompts or try with a clearer use case

### Error: "Access Denied" in S3
- **Cause**: Lambda doesn't have permissions to write to S3
- **Solution**: Verify Lambda role IAM permissions

### Error: "Model not found"
- **Cause**: Nova models aren't available in the region
- **Solution**: Change to `us-east-1` or verify regional availability

---

## 👥 Authors

Angel Moreno, Luis Adames, William Ferreira

## 📄 License

This project is under the MIT license.

---

**Developed for AWS Hackathon 2025** 🚀
