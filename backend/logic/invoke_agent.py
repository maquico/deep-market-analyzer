import json
import uuid
import boto3

def invoke_agent(prompt: str,
                 agent_arn:str = "arn:aws:bedrock-agentcore:us-east-1:444184706474:runtime/deep_market_agent-IpktmbCDc9") -> str:
    
    """Invoke the Bedrock AgentCore agent with the given prompt."""
    # Initialize the AgentCore client
    agent_core_client = boto3.client('bedrock-agentcore')
    
    # Prepare the payload
    payload = json.dumps({"prompt": prompt}).encode()
    
    # Invoke the agent
    response = agent_core_client.invoke_agent_runtime(
        agentRuntimeArn=agent_arn,
        payload=payload
    )

    content = []
    for chunk in response.get("response", []):
        content.append(chunk.decode('utf-8'))

    return json.loads(''.join(content))

if __name__ == "__main__":
    test_prompt = "Hola como estas?."
    response = invoke_agent(test_prompt)
    print(response)
