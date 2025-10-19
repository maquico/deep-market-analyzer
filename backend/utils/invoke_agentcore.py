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
                    if isinstance(line, dict):
                        print("DICT DATA:", line)
                    else:
                        print("LINE DATA:", line)
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
        prompts = ["Hello my name is Angel",
                   #"what are my competitors? My company is a startup in the e-commerce sector specializing in handmade crafts. We focus on unique, artisanal products that appeal to niche markets. Our main competitors are Etsy and local craft fairs.",
                   #"what are my competitors?",
                   #"yes please research them",
                   #"build the report based on that info",
                   #"I want to create a marketing plan to increase brand awareness and drive sales. What strategies should I consider?",
                   #"I would like to create a disruptive new product to compete with Amazon and Etsy.Mainly on the Europe market as I have already a big public on the US. What ideas do you have?",
                   #"Based on our conversation, what are my main business objectives and target markets"
                   #"Check our conv history and then Please build the report again"
                   ]
        for prompt in prompts:
            generator = invoke_agent(prompt=prompt,
                                    session_id="40f812f8-932f-46f6-bff5-3f248e5c4320",
                                    user_id="4d747692-ae0f-498f-a99d-1ce177d0b379",
                                    memory_id="DeepMarketAgentMemoryV2-qlkIPd8YnA")
            async for evt in generator:
                #print(evt)
                if isinstance(evt, str):
                    evt_dict = json.loads(evt)
                elif isinstance(evt, dict):
                    evt_dict = evt
                else:
                    continue
                chunk = evt_dict.get("message", "")
                #print(chunk, end="", flush=True)

    asyncio.run(main())
    