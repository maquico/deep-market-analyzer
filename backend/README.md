# Deep Market Analyzer - Backend

The backend infrastructure for Deep Market Analyzer, built as a serverless microservices architecture on AWS. This system orchestrates an AI agent powered by AWS Bedrock that conducts competitive market analysis through autonomous research, image generation, and report compilation.

## Architecture Overview

The backend follows a **microservices pattern** where each service handles a specific capability:

- **Agent Core**: The brain - orchestrates the entire analysis workflow
- **API Lambda**: Entry point - handles HTTP requests and routes to agent
- **Image Generation**: Creates product visualizations using Amazon Nova Canvas
- **PDF Generation**: Compiles analysis into professional PDF reports
- **Web Search**: Fetches real-time market data via Tavily API

This design provides **independent scaling**, **isolated deployments**, and **clear separation of concerns**.

## Tech Stack

### Core Technologies
- **Python 3.11+** (agent_core, lambda_api, lambda_img_gen, lambda_tavily)
- **Node.js 20+** (lambda_pdf_gen)
- **AWS Lambda** (serverless compute)
- **API Gateway** (HTTP routing)

### AI & Agent Frameworks
- **LangGraph** - Agent workflow orchestration
- **AWS Bedrock Agent Core** - Memory & state management
- **LangChain AWS** - Bedrock integrations
- **Claude 3.7 Sonnet** - Primary reasoning model
- **Amazon Nova Canvas** - Image generation
- **Amazon Nova Pro** - Image prompt enhancement

### Storage & Database
- **DynamoDB** - Conversations, documents, chat history
- **S3** - PDF storage, generated images (presigned URLs)

### APIs & Tools
- **Tavily API** - Web search and content extraction
- **FastAPI** - REST API framework
- **Mangum** - ASGI adapter for Lambda

## Directory Structure

```
backend/
│
├── agent_core/              # AI Agent orchestration
│   ├── deep_market_agent.py # LangGraph agent implementation
│   ├── prompts.py           # System prompts for agent & tools
│   ├── dynamo_handler.py    # Chat persistence
│   ├── Dockerfile           # Container for Agent Core deployment
│   ├── requirements.txt     # LangGraph, Bedrock dependencies
│   └── tools/               # Agent capabilities
│       ├── gen_img.py       # Image generation orchestration
│       ├── gen_pdf.py       # PDF report compilation
│       └── web_search.py    # Tavily search integration
│
├── lambda_api/              # Main API Gateway
│   ├── main.py              # FastAPI app entry point
│   ├── serverless.yml       # Deployment config
│   ├── requirements.txt     # FastAPI, boto3, mangum
│   └── app/
│       ├── routes.py        # HTTP endpoints
│       ├── models.py        # Pydantic schemas
│       └── dynamo.py        # Database operations
│
├── lambda_img_gen/          # Image generation service
│   ├── handler.py           # Bedrock Nova Canvas invocation
│   ├── serverless.yml       # Lambda deployment config
│   └── requirements.txt     # boto3, bedrock-runtime
│
├── lambda_pdf_gen/          # PDF compilation service
│   ├── handler.mjs          # Puppeteer + Handlebars logic
│   ├── package.json         # Node dependencies
│   ├── serverless.yml       # Lambda config with layers
│   └── local_test.mjs       # Local testing script
│
├── lambda_tavily/           # Web search service
│   ├── handler.py           # Tavily API wrapper
│   ├── serverless.yml       # Deployment config
│   └── requirements.txt     # requests, dotenv
│
└── utils/                   # Shared utilities
    ├── dynamo_handler.py    # DynamoDB helpers
    ├── gateway_auth.py      # API authentication
    ├── invoke_agentcore.py  # Agent Core invocation
    └── memory_agentcore.py  # Memory management
```

## How It Works

### Request Flow

1. **Client** sends chat message → **API Gateway** → **lambda_api**
2. **lambda_api** invokes **agent_core** (via Bedrock Agent Core runtime)
3. **Agent Core** (LangGraph) decides which tools to use:
   - Calls **lambda_tavily** for web research
   - Calls **lambda_img_gen** for product visualizations
   - Calls **lambda_pdf_gen** to compile reports
4. **Agent** streams responses back to client in real-time
5. **DynamoDB** stores conversation history
6. **S3** stores generated PDFs and images

### Why This Structure?

**Microservices approach** allows:
- **Independent scaling**: PDF generation can scale separately from search
- **Technology flexibility**: Use Node.js for Puppeteer, Python for AI
- **Isolated failures**: If image generation fails, search still works
- **Faster deployments**: Update one service without touching others
- **Cost optimization**: Each Lambda only runs when needed

**Agent Core as orchestrator**:
- Maintains conversation context across tool calls
- Decides autonomously when to search, generate images, or create reports
- Uses LangGraph for complex multi-step workflows
- Leverages Bedrock Agent Core for persistent memory

## Service Details

### agent_core
- **Purpose**: AI agent brain - decides research strategy and orchestrates tools
- **Tech**: LangGraph + Bedrock Agent Core + Claude 3.7 Sonnet
- **Key Files**: 
  - `deep_market_agent.py` - Agent state machine
  - `prompts.py` - System instructions for agent behavior

### lambda_api
- **Purpose**: HTTP interface for frontend communication
- **Tech**: FastAPI + Mangum (ASGI → Lambda adapter)
- **Endpoints**: Chat messages, session management, document retrieval

### lambda_img_gen
- **Purpose**: Generate product concept images from text descriptions
- **Tech**: Amazon Nova Canvas + Nova Pro (prompt enhancement)
- **Flow**: Text → Enhanced prompt → Image → S3 → Presigned URL

### lambda_pdf_gen
- **Purpose**: Compile analysis into formatted PDF reports
- **Tech**: Puppeteer (headless Chrome) + Handlebars templates
- **Features**: Page breaks, embedded images, professional styling

### lambda_tavily
- **Purpose**: Real-time web research for market data
- **Tech**: Tavily API (search + extraction)
- **Capabilities**: News, statistics, competitor information

## Environment Variables

Each service requires specific environment variables. Check individual service folders for details:
- `AWS_REGION` - AWS region for services
- `S3_BUCKET_NAME` - Storage bucket for files
- `DYNAMO_*_TABLE_NAME` - DynamoDB table names
- `TAVILY_API_KEY` - Tavily search API key
- API endpoints and authentication tokens

## Deployment

Each service can be deployed independently using Serverless Framework or AWS SAM. See respective service folders for:
- Local testing instructions
- Deployment commands
- Configuration requirements

---

**Note**: This backend is designed for AWS Lambda. For local development, see individual service READMEs for setup instructions.