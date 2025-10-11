from bedrock_agentcore import BedrockAgentCoreApp
import boto3
from langgraph.graph import StateGraph, MessagesState
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_aws import ChatBedrock
from bedrock_agentcore.memory import MemoryClient
from prompts import deep_market_agent_v1_prompt
from chat import add_message_to_chat

client = MemoryClient(region_name="us-east-1")

session = boto3.Session()

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
    def list_events():
        """Tool used when needed to retrieve recent information""" 
        events = client.list_events(
                memory_id=memory_id,
                actor_id=actor_id,
                session_id=session_id,
                max_results=10
            )
        return events
        
    
    # Bind tools to the LLM
    tools = [list_events]
    llm_with_tools = llm.bind_tools(tools)
    
    # System message
    system_message = system_message
    
    # Define the chatbot node
    def chatbot(state: MessagesState):
        raw_messages = state["messages"]
    
        # Remove any existing system messages to avoid duplicates or misplacement
        non_system_messages = [msg for msg in raw_messages if not isinstance(msg, SystemMessage)]
    
        # Always ensure SystemMessage is first
        messages = [SystemMessage(content=system_message)] + non_system_messages
    
        latest_user_message = next((msg.content for msg in reversed(messages) if isinstance(msg, HumanMessage)), None)
    
        # Get response from model with tools bound
        response = llm_with_tools.invoke(messages)
    
        # Save conversation if applicable
        if latest_user_message and response.content.strip():  # Check that response has content
            conversation = [
                (latest_user_message, "USER"),
                (response.content, "ASSISTANT")
            ]
            
            # Validate that all message texts are non-empty
            if all(msg[0].strip() for msg in conversation):  # Ensure no empty messages
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
    graph_builder = StateGraph(MessagesState)
    
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

def invoke_langgraph_bedrock(payload, agent):
    """
    Invoke the agent with a payload
    """
    user_input = payload.get("prompt")
    
    # Create the input in the format expected by LangGraph
    response = agent.invoke({"messages": [HumanMessage(content=user_input)]})
    
    # Extract the final message content
    return response["messages"][-1].content

app = BedrockAgentCoreApp()


@app.entrypoint
async def agent_invocation(payload):
    """Handler for agent invocation"""
    agent = create_agent(client, memory_id=payload.get("memory_id"), actor_id=payload.get("user_id"), session_id=payload.get("session_id"))
    user_message = payload.get(
        "prompt", "No prompt found in input, please guide customer to create a json payload with prompt key"
    )
    stream = invoke_langgraph_bedrock(user_message, agent)
    async for event in stream:
        print(event)
        yield (event)


if __name__ == "__main__":
    app.run()
        