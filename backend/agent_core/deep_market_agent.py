from bedrock_agentcore import BedrockAgentCoreApp
from strands import Agent
from strands.models import BedrockModel
import boto3

session = boto3.Session()
# Create a Bedrock model with the custom session
bedrock_model = BedrockModel(
    model_id="us.anthropic.claude-3-7-sonnet-20250219-v1:0",
    boto_session=session
)

app = BedrockAgentCoreApp()
agent = Agent(model=bedrock_model)

@app.entrypoint
async def agent_invocation(payload):
    """Handler for agent invocation"""
    user_message = payload.get(
        "prompt", "No prompt found in input, please guide customer to create a json payload with prompt key"
    )
    stream = agent.stream_async(user_message)
    async for event in stream:
        print(event)
        yield (event)


if __name__ == "__main__":
    app.run()
        