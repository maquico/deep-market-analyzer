import boto3
import json
from typing import Optional
def invoke_agent(prompt: str,
                 #session_id: str,
                 agent_arn:str = "arn:aws:bedrock-agentcore:us-east-1:444184706474:runtime/deep_market_agent-IpktmbCDc9"):
    
    """Invoke the Bedrock AgentCore agent with the given prompt."""
    # Initialize the AgentCore client
    agent_core_client = boto3.client('bedrock-agentcore')
    
    # Prepare the payload
    payload = json.dumps({"prompt": prompt}).encode()
    
    # Invoke the agent
    response = agent_core_client.invoke_agent_runtime(
        agentRuntimeArn=agent_arn,
        #runtimeSessionId=session_id,
        payload=payload
    )

    # Process and print the response
    if "text/event-stream" in response.get("contentType", ""):
        # Handle streaming response
        content = []
        for line in response["response"].iter_lines(chunk_size=10):
            if line:
                line = line.decode("utf-8")
                if line.startswith("data: "):
                    line = line[6:]
                    #print(line)
                    yield line
                    content.append(line)
        #print("\nComplete response:", "\n".join(content))
    elif response.get("contentType") == "application/json":
        # Handle standard JSON response
        content = []
        for chunk in response.get("response", []):
            content.append(chunk.decode('utf-8'))
        return json.loads(''.join(content))


def extract_chunk_from_string(s: str) -> Optional[str]:
    """
    Try to extract a text chunk from a single event string `s`.
    Returns the chunk or None if nothing found.
    """
    try:
        o = json.loads(s)

        if isinstance(o, dict):
            # event -> contentBlockDelta -> delta -> text
            ev = o.get("event") or o
            # contentBlockDelta path
            cbd = ev.get("contentBlockDelta") if isinstance(ev, dict) else None
            if cbd and isinstance(cbd, dict):
                d = cbd.get("delta")
                if d and isinstance(d, dict):
                    t = d.get("text")
                    if t is not None:
                        return t

        # if JSON parsed to something else ignore
    except Exception:
        pass
    # nothing found
    return None


if __name__ == "__main__":
    test_prompt = "Hola como estas?."
    for evt in invoke_agent(test_prompt):
        #print("Event:", evt)
        chunk = extract_chunk_from_string(evt)
        if chunk is not None:
            print("Extracted chunk:", chunk)