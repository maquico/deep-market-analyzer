# Agent Core - The Brain of Deep Market Analyzer 🧠

The **Agent Core** is the autonomous AI agent that powers Deep Market Analyzer. Built with LangGraph and AWS Bedrock Agent Core, it orchestrates complex multi-step workflows, maintains conversation context, and intelligently decides when to research competitors, generate images, or compile reports.

This is where the magic happens—the agent understands user needs, breaks down complex analysis tasks, and autonomously executes research strategies to deliver actionable business intelligence.

## 📋 What Makes This Special

### Autonomous Decision Making
Unlike traditional chatbots that simply respond to prompts, this agent:
- **Thinks strategically** about what information is needed
- **Decides autonomously** which tools to use and when
- **Remembers context** across sessions using persistent memory
- **Adapts its approach** based on user goals and available data

### Multi-Step Reasoning
The agent can execute complex workflows like:
1. User asks about competitor analysis
2. Agent searches chat history to recall company details
3. Agent researches the web for competitor information
4. Agent generates product concept images
5. Agent compiles everything into a professional PDF report

All of this happens automatically with intelligent orchestration.

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Agent Core (LangGraph)                    │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐      ┌──────────────┐      ┌────────────┐│
│  │  Pre-Model   │─────▶│   Chatbot    │─────▶│ Post-Model ││
│  │     Hook     │      │   (Claude)   │      │    Hook    ││
│  └──────────────┘      └──────┬───────┘      └────────────┘│
│         │                     │                       │      │
│         │                     │ Decision              │      │
│         ▼                     ▼                       ▼      │
│  ┌──────────────┐      ┌──────────────┐      ┌────────────┐│
│  │ Save User    │      │  Tool Node   │      │  Save AI   ││
│  │  Message     │      │              │      │  Response  ││
│  └──────────────┘      └──────┬───────┘      └────────────┘│
│                               │                              │
│         ┌─────────────────────┴──────────────────┐         │
│         │         Agent Tools (5 total)           │         │
│         ├──────────────────────────────────────────┤        │
│         │ • search_chat_history                    │        │
│         │ • research_web (Tavily)                  │        │
│         │ • extract_urls (Tavily)                  │        │
│         │ • generate_images (Nova Canvas)          │        │
│         │ • generate_pdf_report (Multi-LLM flow)   │        │
│         └──────────────────────────────────────────┘        │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
         ┌────────────────────────────────┐
         │  AWS Bedrock Agent Core        │
         │  - Memory Management           │
         │  - State Persistence           │
         │  - Session Tracking            │
         └────────────────────────────────┘
```

## 🚀 Project Structure

```
agent_core/
├── deep_market_agent.py    # Main agent implementation (LangGraph)
├── prompts.py              # System prompts for agent & tools
├── dynamo_handler.py       # DynamoDB chat persistence
├── Dockerfile              # Container for Agent Core deployment
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (local)
└── tools/                  # Agent capabilities
    ├── gen_img.py          # Image generation orchestration
    ├── gen_pdf.py          # PDF report compilation flow
    └── web_search.py       # Tavily search & extraction
```

## 📦 Prerequisites

1. **Python 3.11+** installed
2. **AWS Account** with Bedrock access
3. **Bedrock Agent Core** memory configured
4. **DynamoDB tables** for chat storage
5. **Access to AWS services**: Bedrock, DynamoDB, S3, Lambda

## 🔧 Configuration

### 1. Setup Environment

```bash
# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Activate (Linux/Mac)
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file:

```env
AWS_REGION_NAME=us-east-1

# Bedrock Agent Core
MEMORY_ID=your-agent-memory-id

# DynamoDB
DYNAMO_CHATS_TABLE=deep-market-analyzer-chats
DYNAMO_MESSAGES_TABLE=deep-market-analyzer-messages
DYNAMO_DOCUMENTS_TABLE=deep-market-analyzer-documents
DYNAMO_IMAGES_TABLE=deep-market-analyzer-images

# S3 Storage
S3_BUCKET_NAME=your-bucket-name

# Tavily API (for web search)
TAVILY_API_KEY=your-tavily-key
```

## 🧠 How the Agent Works

### The Agent State

The agent maintains state throughout the conversation:

```python
class DeepMarketAgentState(TypedDict):
    messages: Annotated[list, add_messages]  # Conversation history
    user_id: str                             # User identifier
    pdf_document_id: str                     # Generated PDF ID
    pdf_presigned_url: str                   # PDF download link
    images: list                             # Generated images
```

### Agent Workflow

#### 1. **Pre-Model Hook**
Before the LLM processes the message:
- Saves user message to Agent Core memory
- Persists message to DynamoDB
- Can retrieve user preferences (optional)

#### 2. **Chatbot Node (Claude 3.7 Sonnet)**
The main reasoning engine:
- Analyzes user intent
- Decides which tools to use (if any)
- Generates natural language responses
- Uses last 6 messages for context window management

#### 3. **Tool Execution**
If the agent decides to use tools:
- **Conditional routing** based on LLM decision
- Tools execute in parallel when possible
- Results fed back to the LLM for interpretation

#### 4. **Post-Model Hook**
After the LLM generates response:
- Saves AI message to Agent Core memory
- Persists response to DynamoDB
- Maintains conversation continuity

### Tool Descriptions

#### 🔍 `search_chat_history`
**Purpose**: Retrieves information from past conversations

**When Used**:
- User references something mentioned before
- Agent needs context about user's company
- Checking if enough information was provided

**How It Works**:
```python
@tool
def search_chat_history(query: str):
    user_memories_namespace = ("users", actor_id)
    memories = store.search(user_memories_namespace, query=query, limit=10)
    return str(memories)
```

Uses semantic search on Agent Core memory store to find relevant past messages.

---

#### 🌐 `research_web`
**Purpose**: Performs web searches for recent market information

**When Used**:
- User asks for competitor analysis
- Needs recent industry trends
- Requires statistics or market data

**How It Works**:
- Calls Tavily API for web search
- Returns top 5 relevant results with AI-generated summaries
- Includes source URLs for credibility

---

#### 📄 `extract_urls`
**Purpose**: Deep-dives into specific web pages

**When Used**:
- User provides URLs to analyze
- Agent found relevant articles via `research_web`
- Needs detailed content from specific sources

**How It Works**:
- Extracts clean content from up to 10 URLs
- Removes ads, navigation, and boilerplate
- Returns structured text for analysis

---

#### 🎨 `generate_images`
**Purpose**: Creates product concept visualizations

**When Used**:
- User explicitly requests images
- Visualizing product ideas or concepts
- Illustrating competitive positioning

**How It Works**:
1. Calls image generation Lambda (Nova Canvas)
2. Generates 3 variations of the concept
3. Stores images in S3
4. Updates agent state with image references
5. Returns presigned URLs for download

**Special Feature**: Uses `Command` to update state:
```python
return Command(update={
    "messages": [ToolMessage(content="Images generated successfully.")],
    "images": images
})
```

---

#### 📊 `generate_pdf_report`
**Purpose**: Compiles conversation into professional PDF report

**When Used**:
- User requests a report or document
- Analysis is complete and ready to export

**How It Works** (Multi-Step Flow):

1. **Extract Conversation**
   - Uses Claude 3.7 Sonnet to summarize full conversation
   - Focuses only on query-relevant information
   - Removes meta-discussion and artifacts

2. **Generate Image Queries**
   - Creates descriptive prompts for report illustrations
   - Based on extracted content themes

3. **Generate Images** (if needed)
   - Calls Nova Canvas for report visuals
   - 3 images matching report sections

4. **Structure Report**
   - Uses Claude to create JSON payload
   - 3 highlights with titles, subtitles, paragraphs
   - Executive summary and closing

5. **Compile PDF**
   - Calls PDF Lambda with Handlebars template
   - Embeds generated images
   - Professional formatting

6. **Store & Return**
   - Saves to DynamoDB documents table
   - Uploads to S3
   - Returns presigned URL

**Complexity**: This is the most sophisticated tool, orchestrating multiple LLM calls and services.

---

## 🎯 Agent Prompting Strategy

### System Prompt Philosophy

The agent uses a carefully crafted system prompt:

```python
deep_market_agent_v1_prompt = """
You are DeepMarketAgent, an AI specialized in deep market analysis.
Your role is to assist users by providing insights, answering questions, 
and generating reports based on market data.

If the user asks for anything that requires specific knowledge about their 
company, check if they have provided enough info using the search_chat_history 
tool, if not make sure to ask for details about their company first.

Avoid executing more than ONE tool consecutively.
When generating a report, the frontend will handle the file presentation, 
if the tool returned an id just tell the user that the report is ready.
Avoid making up answers. If you don't know, say "I don't know".
"""
```

**Key Principles**:
1. **Context awareness**: Check history before asking repeat questions
2. **Tool discipline**: One tool at a time to avoid complexity
3. **Honesty**: Admit when information is unknown
4. **User-friendly**: Simple communication about complex operations

### Sub-Agent Prompts

The PDF generation flow uses specialized prompts for each step:

- **`messages_extraction_v1_prompt`**: Summarizes conversation for report
- **`images_query_generation_v1_prompt`**: Creates image descriptions
- **`pdf_parser_v1_prompt`**: Structures report JSON

Each prompt is tuned for its specific task with clear instructions and examples.

## 💡 Key Features

### Persistent Memory

Uses **AWS Bedrock Agent Core** for:
- **Long-term memory**: Remembers user details across sessions
- **Semantic search**: Finds relevant past information
- **Namespace organization**: Separates user data (`users`, `actor_id`, `thread_id`)

```python
checkpointer = AgentCoreMemorySaver(memory_id=memory_id)
store = AgentCoreMemoryStore(memory_id=memory_id)
```

### Streaming Responses

Real-time token-by-token streaming:

```python
async def stream_invoke_langgraph_agent(payload, agent):
    async for event in agent.astream_events(...):
        if event["event"] == "on_chat_model_stream":
            chunk = data["chunk"].content[0]["text"]
            yield {"message": chunk}
```

Frontend sees the agent "thinking" in real-time.

### State Management

The agent tracks multiple pieces of state:
- Conversation messages (with add_messages reducer)
- User ID for personalization
- Generated artifacts (PDFs, images)
- Tool execution results

### Error Handling

Graceful degradation:
- Tool failures don't crash the agent
- Returns error messages to LLM for interpretation
- Continues conversation even if tools fail

## ⚙️ Technical Details

### AI Models Used

| Model | Purpose | Temperature | Why This Model |
|-------|---------|-------------|----------------|
| **Claude 3.7 Sonnet** | Main reasoning | 0.1 | Best for complex reasoning, tool use, and business analysis |
| **Claude 3.7 Sonnet** | Report extraction | 0.3 | Balanced creativity for summarization |
| **Claude 3.7 Sonnet** | Report structuring | 0.3 | JSON generation reliability |
| **Nova Canvas** | Image generation | N/A | AWS native, high-quality product images |
| **Nova Pro** | Image prompts | N/A | Enhanced prompt generation |

### LangGraph Components

- **StateGraph**: Manages agent workflow
- **ToolNode**: Handles tool execution
- **tools_condition**: Routes based on LLM decisions
- **Checkpointer**: Saves conversation state
- **Memory Store**: Persistent semantic storage

### AWS Services Integration

- **Bedrock**: LLM inference (Claude, Nova)
- **Agent Core**: Memory management and state
- **DynamoDB**: Message persistence
- **S3**: File storage (PDFs, images)
- **Lambda**: Tool execution (images, PDFs, search)

### Performance Optimization

1. **Context Window Management**: Only last 6 messages to reduce tokens
2. **Parallel Tool Execution**: When tools don't depend on each other
3. **Streaming**: Immediate user feedback
4. **Caching**: Agent Core memory reduces redundant queries

## 🚢 Deployment

### Using Bedrock Agent Core App

```python
app = BedrockAgentCoreApp()

@app.entrypoint
async def agent_invocation(payload):
    payload = json.loads(payload) if isinstance(payload, str) else payload
    agent = create_agent(...)
    async for event in stream_invoke_langgraph_agent(payload, agent):
        yield event

if __name__ == "__main__":
    app.run()
```

### Deployment Options

1. **AWS Lambda**: Serverless deployment (recommended)
2. **ECS/Fargate**: Containerized deployment
3. **Local**: Development and testing

### Environment Variables

```bash
# Required
AWS_REGION_NAME=us-east-1
MEMORY_ID=your-memory-id

# DynamoDB
DYNAMO_CHATS_TABLE=table-name
DYNAMO_MESSAGES_TABLE=table-name
DYNAMO_DOCUMENTS_TABLE=table-name
DYNAMO_IMAGES_TABLE=table-name

# S3
S3_BUCKET_NAME=bucket-name

# APIs
TAVILY_API_KEY=your-key
```

## 🔄 Agent Execution Flow

### Example: Competitor Analysis Request

```
User: "Compare my SaaS product to Competitor X"
   │
   ▼
Pre-Model Hook
   │ Save message to memory
   │ Save to DynamoDB
   ▼
Claude 3.7 Sonnet (Chatbot)
   │ Analyze: Need company info
   │ Decision: Use search_chat_history
   ▼
Tool: search_chat_history("user company details")
   │ Returns: Company name, product, target market
   ▼
Claude 3.7 Sonnet
   │ Analyze: Have company info, need competitor data
   │ Decision: Use research_web
   ▼
Tool: research_web("Competitor X features pricing market")
   │ Returns: Recent articles, pricing, features
   ▼
Claude 3.7 Sonnet
   │ Synthesize comparison
   │ Generate response
   ▼
Post-Model Hook
   │ Save AI response to memory
   │ Save to DynamoDB
   ▼
Stream to Frontend
```

### Example: Report Generation Request

```
User: "Generate a report with this analysis"
   │
   ▼
Claude decides: Use generate_pdf_report
   │
   ▼
Tool: generate_pdf_report
   │
   ├─▶ Sub-LLM: Extract conversation
   │      │ Input: Full message history
   │      └─▶ Output: Summarized content
   │
   ├─▶ Sub-LLM: Generate image queries
   │      │ Input: Extracted content
   │      └─▶ Output: 3 image descriptions
   │
   ├─▶ Lambda: Generate images
   │      │ Input: Image descriptions
   │      └─▶ Output: 3 images in S3
   │
   ├─▶ Sub-LLM: Structure report
   │      │ Input: Content + images
   │      └─▶ Output: JSON payload
   │
   └─▶ Lambda: Compile PDF
          │ Input: JSON + template
          └─▶ Output: PDF in S3, presigned URL
   │
   ▼
Agent State Updated
   │ pdf_document_id
   │ pdf_presigned_url
   ▼
Frontend displays download button
```

## 🐛 Troubleshooting

### Agent doesn't use tools
- **Cause**: Prompt not clear about when to use tools
- **Solution**: Check tool docstrings, update system prompt

### Memory not persisting
- **Cause**: Incorrect memory_id or Actor Core configuration
- **Solution**: Verify `MEMORY_ID` and Agent Core setup

### Tools timing out
- **Cause**: Lambda cold starts or complex operations
- **Solution**: Increase Lambda timeout, optimize tool logic

### Conversation context lost
- **Cause**: State not being saved properly
- **Solution**: Check pre/post model hooks, verify DynamoDB writes

## 📚 References

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [AWS Bedrock Agent Core](https://docs.aws.amazon.com/bedrock/latest/userguide/agents.html)
- [Claude 3.7 Sonnet](https://www.anthropic.com/claude)
- [Tavily API](https://tavily.com/)

## 👥 Authors

Angel Moreno, Luis Adames, William Ferreira

## 📄 License

This project is under the MIT license.

---

**Developed for AWS Hackathon 2025** 🚀

**This is the brain. This is where intelligence happens.**