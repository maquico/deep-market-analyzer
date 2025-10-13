from bedrock_agentcore import BedrockAgentCoreApp
import boto3
from langgraph.graph import StateGraph, MessagesState
from langgraph.prebuilt import ToolNode, tools_condition, InjectedState
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langgraph.graph.message import add_messages
from typing import TypedDict, Annotated
from langchain_aws import ChatBedrock
from bedrock_agentcore.memory import MemoryClient
from prompts import deep_market_agent_v1_prompt
from chat import add_message_to_chat
from tools.gen_img import invoke_via_api_gateway
import json

client = MemoryClient(region_name="us-east-1")

session = boto3.Session()

class DeepMarketAgentState(TypedDict):
    # Messages have the type "list". The `add_messages` function
    # in the annotation defines how this state key should be updated
    # (in this case, it appends messages to the list, rather than overwriting them)
    messages: Annotated[list, add_messages]
    user_id: str

def create_agent(client,
                 memory_id,
                 actor_id,
                 session_id,
                 model_id="us.anthropic.claude-3-7-sonnet-20250219-v1:0",
                 temperature=0.1, system_message=deep_market_agent_v1_prompt):
    """Create and configure the LangGraph agent"""
    
    # Initialize your LLM (adjust model and parameters as needed)
    llm = ChatBedrock(
        model_id=model_id,
        model_kwargs={"temperature": temperature}
    )
    
    @tool
    def list_recent_messages():
        """Tool used when needed to retrieve recent information from chat history""" 
        events = client.list_events(
                memory_id=memory_id,
                actor_id=actor_id,
                session_id=session_id,
                max_results=10
            )
        #print("EVENTS: ", events)
        return events
    
    @tool
    def search_chat_history(query: str, memory_id: str = memory_id, actor_id: str = actor_id):
        """Tool used when needed to retrieve general and important information from chat history. 
        Formulate the query based on what you want to know about the user""" 
        
        memories = client.retrieve_memories(
                    memory_id=memory_id,
                    namespace=f"/users/{actor_id}",
                    query=query
                )
        
        #print("MEMORIES: ", memories)
        if not memories:
            memories = "No relevant memories found."
        return str(memories)
    
    @tool
    def generate_image(image_description: str, user_id: str = actor_id):
        """Tool used to generate an image based on user input about products or services ideas.
        Use this tool:
        - If the user explicitly requests an image.
        - Before generating a report, document, or pdf to include images in it.""" 
        result = invoke_via_api_gateway(use_case=image_description, user_id=user_id)  
        return result 
        
    
    # Bind tools to the LLM
    tools = [search_chat_history, list_recent_messages, generate_image]
    llm_with_tools = llm.bind_tools(tools)
    
    # System message
    system_message = system_message
    
    # Define the chatbot node
    def chatbot(state: DeepMarketAgentState):
        raw_messages = state["messages"]
    
        # Remove any existing system messages to avoid duplicates or misplacement
        non_system_messages = [msg for msg in raw_messages if not isinstance(msg, SystemMessage)]
    
        # Always ensure SystemMessage is first
        messages = [SystemMessage(content=system_message)] + non_system_messages
    
        latest_user_message = next((msg.content for msg in reversed(messages) if isinstance(msg, HumanMessage)), None)

        #print("LATEST USER MESSAGE: ", latest_user_message)
        # Get response from model with tools bound
        response = llm_with_tools.invoke(messages)
    
        # Save conversation if applicable
        response_final_content = response.content[0].get("text", "").strip() if response.content else ""
        #print("RESPONSE CONTENT: ", response.content)
        if latest_user_message and response_final_content.strip():  # Check that response has content
            conversation = [
                (latest_user_message, "USER"),
                (response_final_content, "ASSISTANT")
            ]
            
            # Validate that all message texts are non-empty
            #print("CONVERSATION: ", conversation)
            if all(msg[0].strip() for msg in conversation):  # Ensure no empty messages
                #print("SAVING CONVERSATION TO AGENTCORE MEMORY: ", conversation)
                try:
                    client.create_event(
                        memory_id=memory_id,
                        actor_id=actor_id,
                        session_id=session_id,
                        messages=conversation
                    )
                except Exception as e:
                    print(f"Error saving conversation: {str(e)}")


                # Add to dynamo db table
                try:
                    chat_id = session_id
                    for msg in conversation:
                        final_message = {"content": msg[0], "sender": msg[1]}
                        add_message_to_chat(chat_id, final_message)
                except Exception as e:
                    print(f"Error saving to DynamoDB: {str(e)}")
                
        
        # Append response to full message history
        return {"messages": raw_messages + [response]}
    
    # Create the graph
    graph_builder = StateGraph(DeepMarketAgentState)
    
    # Add nodes
    graph_builder.add_node("chatbot", chatbot)
    graph_builder.add_node("tools", ToolNode(tools))
    
    # Add edges
    graph_builder.add_conditional_edges(
        "chatbot",
        tools_condition,
    )
    graph_builder.add_edge("tools", "chatbot")
    
    # Set entry point
    graph_builder.set_entry_point("chatbot")
    
    # Compile the graph
    return graph_builder.compile()

def invoke_langgraph_agent(payload, agent):
    """
    Invoke the agent with a payload
    """
    user_input = payload.get("prompt")

    state = {
        "messages": [HumanMessage(content=user_input)],
        "user_id": payload.get("user_id", "unknown_user")
    }
    
    # Create the input in the format expected by LangGraph
    response = agent.invoke(state)
    
    # Extract the final message content
    return response["messages"][-1].content

async def stream_invoke_langgraph_agent(payload, agent):
    """
    Stream invoke the agent with a payload
    """
    user_input = payload.get("prompt")
    nodes_to_stream = ["chatbot"]
    async for event in agent.astream_events({"messages": [HumanMessage(content=user_input)]}):
        if event["event"] == "on_chat_model_stream" and event["metadata"].get("langgraph_node", '') in nodes_to_stream:
            data = event["data"]
            #print("DATA: ", data)
            chunk = ""
            if data["chunk"].content:
                if data["chunk"].content[0].get("text", None):
                    chunk = data["chunk"].content[0]["text"]
                    #print("CHUNK: ", chunk)

            yield json.dumps({"message": chunk})


app = BedrockAgentCoreApp()

@app.entrypoint
async def agent_invocation(payload):
    """Handler for agent invocation"""
    payload = json.loads(payload) if isinstance(payload, str) else payload
    agent = create_agent(client, memory_id=payload.get("memory_id"), actor_id=payload.get("user_id"), session_id=payload.get("session_id"))
    async for event in stream_invoke_langgraph_agent(payload=payload, agent=agent):
        yield (event)

if __name__ == "__main__":
    app.run()
        

