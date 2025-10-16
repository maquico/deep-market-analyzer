from logging import config
from bedrock_agentcore import BedrockAgentCoreApp
import boto3
from langgraph.graph import StateGraph, MessagesState
from langgraph.prebuilt import ToolNode, tools_condition, InjectedState
from langchain_core.tools import tool
from langchain_core.runnables import RunnableConfig
from langchain_core.stores import BaseStore
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, ToolMessage
from langgraph.graph.message import add_messages
from langgraph_checkpoint_aws import AgentCoreMemorySaver, AgentCoreMemoryStore
from typing import TypedDict, Annotated
from langchain_aws import ChatBedrock
from bedrock_agentcore.memory import MemoryClient
from prompts import deep_market_agent_v1_prompt
from chat import add_message_to_chat
from tools.gen_img import invoke_via_api_gateway
from dotenv import load_dotenv
import json
import uuid

load_dotenv()
AWS_REGION_NAME = "us-east-1"
client = MemoryClient(region_name=AWS_REGION_NAME)

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

    checkpointer = AgentCoreMemorySaver(memory_id=memory_id, region_name=AWS_REGION_NAME)
    store = AgentCoreMemoryStore(memory_id=memory_id, region_name=AWS_REGION_NAME)

    def pre_model_hook(state, config: RunnableConfig, *, store: BaseStore = store):
        """Hook that runs pre-LLM invocation to save the latest human message"""
        actor_id = config["configurable"]["actor_id"]
        thread_id = config["configurable"]["thread_id"]

        # Saving the message to the actor and session combination that we get at runtime
        namespace = (actor_id, thread_id)

        messages = state.get("messages", [])
        # Save the last human message we see before LLM invocation
        for msg in reversed(messages):
            if isinstance(msg, HumanMessage):
                store.put(namespace, str(uuid.uuid4()), {"message": msg})
                final_message = {"content": msg.content, "sender": "USER"}
                add_message_to_chat(session_id, final_message)
                break

        # OPTIONAL: Retrieve user preferences based on the last message and append to state
        #user_memories_namespace = ("users", actor_id)
        #memories = store.search(user_memories_namespace, query=msg.content, limit=5)
        # # Add to input messages as needed

        return {"messages": messages}
    
    def post_model_hook(state, config: RunnableConfig, *, store: BaseStore = store):
        """Hook that runs post-LLM invocation to save the latest AI and Tools message"""
        actor_id = config["configurable"]["actor_id"]
        thread_id = config["configurable"]["thread_id"]

        # Saving the message to the actor and session combination that we get at runtime
        namespace = (actor_id, thread_id)

        messages = state.get("messages", [])
        # Save the last human message we see before LLM invocation
        for msg in reversed(messages):
            if isinstance(msg, AIMessage):
                store.put(namespace, str(uuid.uuid4()), {"message": msg})
                final_message = {"content": msg.content, "sender": "ASSISTANT"}
                add_message_to_chat(session_id, final_message)
                break

        return {"messages": messages}
    
    @tool
    def search_chat_history(query: str):
        """Tool used when needed to retrieve general and important information from chat history. 
        Formulate the query based on what you want to know about the user""" 
        
        user_memories_namespace = ("users", actor_id)
        memories = store.search(user_memories_namespace, query=query, limit=10)
        return str(memories)
    
    @tool
    def generate_image(image_description: str):
        """Tool used to generate an image based on user input about products or services ideas.
        Use this tool:
        - If the user explicitly requests an image.
        - Before generating a report, document, or pdf to include images in it.""" 
        result = invoke_via_api_gateway(use_case=image_description, user_id=actor_id)  
        return result 
        
    
    # Bind tools to the LLM
    tools = [search_chat_history, generate_image]
    llm_with_tools = llm.bind_tools(tools)
    
    # System message
    system_message = system_message
    
    # Define the chatbot node
    def chatbot(state: DeepMarketAgentState):
        raw_messages = state["messages"]
    
        # Remove any existing system messages to avoid duplicates or misplacement
        non_system_messages = [msg for msg in raw_messages if not isinstance(msg, SystemMessage)]
    
        # Always ensure SystemMessage is first
        messages = [SystemMessage(content=system_message)] + non_system_messages[-6:]  # Limit to last 6 messages for context
    
        # Get response from model with tools bound
        response = llm_with_tools.invoke(messages
                                         #config={"configurable": {"actor_id": actor_id, "thread_id": session_id}}
                                         )
    
        # Append response to full message history
        return {"messages": raw_messages + [response]}
    
    # Create the graph
    graph_builder = StateGraph(DeepMarketAgentState)
    
    # Add nodes
    graph_builder.add_node("pre_model_hook", pre_model_hook)
    graph_builder.add_node("chatbot", chatbot)
    graph_builder.add_node("post_model_hook", post_model_hook)
    graph_builder.add_node("tools", ToolNode(tools))
    
    # Add edges
    graph_builder.add_conditional_edges(
        "chatbot",
        tools_condition,
    )
    graph_builder.add_edge("pre_model_hook", "chatbot")
    graph_builder.add_edge("chatbot", "post_model_hook")
    graph_builder.add_edge("tools", "pre_model_hook")
    
    # Set entry point
    graph_builder.set_entry_point("pre_model_hook")
    
    # Compile the graph
    return graph_builder.compile(store=store,
                                 checkpointer=checkpointer)

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
    actor_id = payload.get("user_id", "unknown_user")
    session_id = payload.get("session_id", "default_session")
    nodes_to_stream = ["chatbot"]
    async for event in agent.astream_events({"messages": [HumanMessage(content=user_input)]},
                                            config={"configurable": {"actor_id": actor_id, "thread_id": session_id}}):
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
        yield event

if __name__ == "__main__":
    app.run()
        

