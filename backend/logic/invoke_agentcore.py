import boto3
import json
from typing import Optional

async def invoke_agent(prompt: str,
                 session_id: str,
                 user_id: str,
                 memory_id: str,
                 agent_arn:str = "arn:aws:bedrock-agentcore:us-east-1:444184706474:runtime/deep_market_agent-IpktmbCDc9"):
    
    """Invoke the Bedrock AgentCore agent with the given prompt."""
    # Initialize the AgentCore client
    agent_core_client = boto3.client('bedrock-agentcore')
    
    # Prepare the payload
    payload = json.dumps({"prompt": prompt,
                          "session_id": session_id,
                          "user_id": user_id,
                          "memory_id": memory_id}).encode()
    
    # Invoke the agent
    response = agent_core_client.invoke_agent_runtime(
        agentRuntimeArn=agent_arn,
        runtimeSessionId=session_id,
        payload=payload
    )
    
    # Process and print the response
    if "text/event-stream" in response.get("contentType", ""):
        print("Streaming response received")
        for line in response["response"].iter_lines(chunk_size=1):
            if line:
                line = line.decode("utf-8")
                if line.startswith("data: "):
                    line = line[6:]
                    yield json.loads(line)
    else:
        print("Non-streaming response received")
        try:
            events = []
            for event in response.get("response", []):
                events.append(event)
        except Exception as e:
            events = [f"Error reading EventStream: {e}"]


if __name__ == "__main__":
    import asyncio
    async def main():
        test_prompt = "Hola como estas?."
        generator = invoke_agent(prompt=test_prompt,
                                session_id="c6a64974-0d21-4991-b324-99d26ca26697",
                                user_id="angel27",
                                memory_id="DeepMarketAgentMemory-39N8xi7C7F")
        async for evt in generator:
            evt_dict = json.loads(evt)
            chunk = evt_dict.get("message", "")
            print(chunk, end="", flush=True)

    asyncio.run(main())
    