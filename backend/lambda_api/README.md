# Lambda API Service

FastAPI-based REST API that serves as the main gateway for the Deep Market Analyzer application. Handles chat management, agent communication, document retrieval, and integrates with AWS Secrets Manager for secure credential management.

## 📋 Features

- **🚀 FastAPI Framework**: High-performance async API with automatic documentation
- **🔐 AWS Secrets Manager**: Secure credential management for production
- **💾 DynamoDB Integration**: NoSQL database for chats, messages, and documents
- **🤖 Agent Communication**: Real-time streaming with Bedrock Agent Core
- **� CORS Support**: Configured for frontend integration
- **📚 Auto Documentation**: Swagger UI and ReDoc built-in
- **🔄 API Versioning**: v1 routing structure
- **⚡ Async Operations**: Non-blocking I/O for better performance

## 🚀 Project Structure

```
lambda_api/
├── main.py                  # Application entry point
├── config.py               # ⭐ Centralized configuration (Secrets Manager + .env)
├── requirements.txt        # Python dependencies
├── serverless.yml          # Serverless Framework deployment config
├── .env.example            # Environment variables template
├── SECRETS_SETUP.md        # AWS Secrets Manager setup guide
└── app/
    ├── __init__.py
    ├── models.py           # Pydantic data models
    ├── dynamo.py           # DynamoDB client configuration
    └── api/
        └── v1/
            ├── api.py      # Main v1 router
            ├── chats.py    # Chat management endpoints
            ├── agent.py    # Agent communication endpoints
            ├── messages.py # Message retrieval endpoints
            ├── documents.py# Document access endpoints
            ├── images.py   # Image retrieval endpoints
            └── users.py    # User management endpoints
```

## 📦 Prerequisites

1. **Python 3.11+** installed
2. **AWS CLI** configured with credentials
3. **AWS Secrets Manager** (for production) or `.env` file (for local)
4. **DynamoDB tables** created (see deployment docs)

## � Configuration

### 1. Clone and setup virtual environment

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows (PowerShell):
.venv\Scripts\activate

# Linux/Mac:
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

#### For Local Development (using .env)

Create a `.env` file in the project root:

```env
ENVIRONMENT=development
AWS_REGION=us-east-1

# DynamoDB Tables
DYNAMO_CHATS_TABLE=deep-market-analyzer-chats
DYNAMO_MESSAGES_TABLE=deep-market-analyzer-messages
DYNAMO_DOCUMENTS_TABLE=deep-market-analyzer-documents
DYNAMO_IMAGES_TABLE=deep-market-analyzer-images

# Agent Core
AGENT_CORE_MEMORY_ID=your-memory-id
BEDROCK_AGENT_ID=your-agent-id
BEDROCK_AGENT_ALIAS_ID=your-alias-id
```

#### For Production (using AWS Secrets Manager)

Set environment variables to point to Secrets Manager:

```bash
export ENVIRONMENT=production
export AWS_SECRET_NAME=hackaton-api-secrets
```

**📖 See [SECRETS_SETUP.md](SECRETS_SETUP.md) for complete Secrets Manager configuration guide.**

### Why This Architecture?

**Development**: Uses `.env` files for quick local iteration without AWS costs.

**Production**: Uses AWS Secrets Manager for:
- ✅ **Security**: No credentials in code or environment
- ✅ **Rotation**: Automatic secret rotation support
- ✅ **Auditing**: CloudTrail tracks all access
- ✅ **Centralization**: Single source of truth for all services

The `config.py` module automatically detects the environment and loads secrets from the appropriate source.

## 🏃 Running the Application

### Local Development

```bash
# Make sure virtual environment is activated
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Start the development server
uvicorn main:app --reload --host localhost --port 3000
```

The API will be available at: **`http://localhost:3000`**

### Interactive Documentation

- **Swagger UI**: `http://localhost:3000/docs`
- **ReDoc**: `http://localhost:3000/redoc`

### Production

Set the environment variables and deploy via Serverless Framework:

```bash
serverless deploy
```

## 📡 API Endpoints

### Core Endpoints

#### Health Check
```
GET /
GET /health
```
Simple health check endpoints to verify the API is running.

#### Agent Communication
```
POST /api/v1/agent/message_with_bot
POST /api/v1/agent/message_with_bot_stream
```
Send messages to the AI agent. The streaming endpoint returns real-time responses.

**Request Body:**
```json
{
  "prompt": "Tell me about my competitors",
  "user_id": "user123",
  "session_id": "chat456"
}
```

#### Chat Management
```
GET    /api/v1/chats              # List all chats
GET    /api/v1/chats/{chat_id}    # Get specific chat
GET    /api/v1/chats/user/{user_id}  # Get user's chats
POST   /api/v1/chats              # Create new chat
PATCH  /api/v1/chats/{chat_id}    # Update chat name
DELETE /api/v1/chats/{chat_id}    # Delete chat
```

#### Documents & Images
```
GET /api/v1/documents/chat/{chat_id}    # Get chat documents
GET /api/v1/documents/user/{user_id}    # Get user documents
GET /api/v1/images/chat/{chat_id}       # Get chat images
GET /api/v1/images/user/{user_id}       # Get user images
```

### Complete API Reference

For a complete list of all endpoints with request/response schemas, visit:
**`http://localhost:3000/docs`** after starting the server.

## 🔐 Secrets Management

### Development Environment

The API uses `.env` files for local development:

```python
# config.py automatically loads from .env
from dotenv import load_dotenv
load_dotenv()
```

**Never commit `.env` files to version control!**

### Production Environment

Uses AWS Secrets Manager with automatic secret loading:

```python
# config.py detects ENVIRONMENT=production
# and fetches secrets from AWS Secrets Manager
import boto3

secrets_client = boto3.client('secretsmanager')
secret = secrets_client.get_secret_value(SecretId=AWS_SECRET_NAME)
```

### Setting Up Secrets Manager

1. Create secret in AWS Secrets Manager:
```bash
aws secretsmanager create-secret \
  --name hackaton-api-secrets \
  --secret-string '{
    "DYNAMO_CHATS_TABLE": "your-table",
    "AGENT_CORE_MEMORY_ID": "your-memory-id"
  }'
```

2. Grant Lambda IAM permissions:
```json
{
  "Effect": "Allow",
  "Action": [
    "secretsmanager:GetSecretValue"
  ],
  "Resource": "arn:aws:secretsmanager:*:*:secret:hackaton-api-secrets-*"
}
```

See **[SECRETS_SETUP.md](SECRETS_SETUP.md)** for detailed instructions.

## 🚢 Deployment

### Deploy to AWS Lambda

```bash
# Deploy to dev
serverless deploy

# Deploy to production
serverless deploy --stage prod
```

### Environment Variables for Lambda

Configure in `serverless.yml` or AWS Console:
```yaml
environment:
  ENVIRONMENT: production
  AWS_SECRET_NAME: hackaton-api-secrets
```

### IAM Permissions Required

```yaml
- dynamodb:GetItem
- dynamodb:PutItem
- dynamodb:Query
- dynamodb:Scan
- dynamodb:UpdateItem
- dynamodb:DeleteItem
- secretsmanager:GetSecretValue
- bedrock:InvokeAgent
- bedrock:InvokeModel
```

## 💡 Use Cases

### Chat Session Management
- Create and manage analysis sessions
- Track conversation history
- Retrieve past analyses

### Agent Integration
- Send prompts to AI agent
- Stream real-time responses
- Handle tool invocations (search, images, PDFs)

### Document & Image Access
- Retrieve generated PDF reports
- Access product concept images
- Filter by user or chat session

### Multi-tenant Support
- User-based data isolation
- Per-user chat histories
- Secure credential management

## ⚙️ Technical Details

### Framework & Runtime
- **Framework**: FastAPI 0.104.1
- **ASGI Server**: Uvicorn
- **Python**: 3.11+
- **Lambda Adapter**: Mangum (for AWS Lambda deployment)

### Database
- **Primary**: DynamoDB (NoSQL)
- **Tables**: Chats, Messages, Documents, Images
- **Indexes**: GSI for user-based queries

### Authentication
- API Gateway authentication (in production)
- CORS configured for frontend origin

### Performance
- Async/await for non-blocking operations
- Connection pooling for DynamoDB
- Streaming responses for agent communication

## 🧪 Testing

```bash
# Run tests (when available)
pytest

# With coverage
pytest --cov=app

# Specific test file
pytest tests/test_chats.py
```

## � Adding New Endpoints

1. Create a new router file in `app/api/v1/`:
```python
# app/api/v1/analytics.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/summary")
def get_summary():
    return {"summary": "data"}
```

2. Register in `app/api/v1/api.py`:
```python
from app.api.v1 import analytics

api_router.include_router(
    analytics.router, 
    prefix="/analytics", 
    tags=["analytics"]
)
```

3. Endpoints will be available at `/api/v1/analytics/summary`

## 🐛 Troubleshooting

### Error: "Secret not found"
- **Cause**: AWS Secrets Manager secret doesn't exist or wrong name
- **Solution**: Verify `AWS_SECRET_NAME` matches the secret in Secrets Manager

### Error: "Access Denied" to DynamoDB
- **Cause**: Lambda role lacks DynamoDB permissions
- **Solution**: Add required permissions to Lambda execution role

### Error: "CORS error" in browser
- **Cause**: Frontend origin not in allowed origins
- **Solution**: Update CORS configuration in `main.py`

### Local server won't start
- **Cause**: Port 3000 already in use or missing dependencies
- **Solution**: Use different port or check virtual environment activation

## 👥 Authors

William Ferreira, Luis Adames, Angel Moreno

## 📄 License

This project is under the MIT license.

---

**Developed for AWS Hackathon 2025** 🚀
