import boto3
import os
import uuid
import datetime
import json
from fastapi import APIRouter, HTTPException
from app.models import MessageRequest, MessageResponse
from app.dynamo import (
    chats_table,
    messages_table
)
from config import Config

config = Config()


router = APIRouter()

async def invoke_agent(prompt: str,
                 session_id: str,
                 user_id: str,
                 memory_id: str,
                 agent_arn:str = config.ARN_BEDROCK_AGENTCORE):
    
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


@router.post("/message_with_bot", response_model=MessageResponse)
async def message_with_bot(request: MessageRequest):
    """Handle a message request and interact with the Bedrock AgentCore agent."""
    print(f"Received request: {request} on the date {datetime.datetime.now().isoformat()}")

    if not request.query:
        raise HTTPException(status_code=400, detail="Query is required")
    
    # Generate unique IDs
    chat_id = request.chat_id or str(uuid.uuid4())
    user_id = request.user_id or "default_user"
    
    # Create a new chat if chat_id was not provided
    if not request.chat_id:
        chats_table.put_item(Item={
            "chat_id": chat_id,
            "chat_name": request.chat_name or "New Chat",
            "user_id": user_id,
            "created_at": datetime.datetime.now().isoformat()
        })
    
    # # Store the user's message
    # messages_table.put_item(Item={
    #     "message_id": message_id,
    #     "chat_id": chat_id,
    #     "created_at": datetime.datetime.now().isoformat(),
    #     "sender": "USER",
    #     "content": request.query
    # })
    
    # Invoke the agent and get the response
    
    try:
        response_text = ""
        async for evt in invoke_agent(
            prompt=request.query,
            session_id=chat_id,
            user_id=user_id,
            memory_id=config.MEMORY_ID_BEDROCK_AGENT_CORE
        ):
            # Process event - can be string or dict
            if isinstance(evt, str):
                evt_dict = json.loads(evt)
            elif isinstance(evt, dict):
                evt_dict = evt
            else:
                continue
            
            # Extract message chunk
            chunk = evt_dict.get("message", "")
            if chunk:
                response_text += chunk
        
        if not response_text:
            response_text = "No response from agent."
        
        # # Store the agent's response
        # response_message_id = str(uuid.uuid4())
        # messages_table.put_item(Item={
        #     "message_id": response_message_id,
        #     "chat_id": chat_id,
        #     "created_at": datetime.datetime.now().isoformat(),
        #     "sender": "ASSISTANT",
        #     "content": response_text
        # })
        
        return MessageResponse(
            message=response_text,
            chat_id=chat_id,
            success=True,
            user_id=user_id,
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error invoking agent: {str(e)}")