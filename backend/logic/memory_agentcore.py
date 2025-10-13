from bedrock_agentcore.memory import MemoryClient

client = MemoryClient(region_name="us-east-1")

def create_memory(name: str = "DeepMarketAgentMemory",
                  description: str = "Memory for deep market analysis conversations"):
    """Create a memory for the Deep Market Agent."""
    memory = client.create_memory(
        name=name,
        description=description,
    )
    return memory

def create_long_term_memory(
    name: str,
    memory_execution_role_arn: str,
    custom_prompt: str,
    model_id: str = "anthropic.claude-3-7-sonnet-20250219-v1:0",
    namespaces: list = None
):
    """
    Creates a long-term memory using a predefined Bedrock AgentCore client.

    Parameters
    ----------
    name : str
        The logical name for the memory (e.g. "AirlineMemoryAgent").
    memory_execution_role_arn : str
        The IAM Role ARN that allows the memory to execute.
    custom_prompt : str
        The custom prompt guiding the extraction process.
    model_id : str, optional
        The model used for preference extraction (default: Claude 3.5 Sonnet).
    namespaces : list, optional
        List of namespaces to scope the memory (default: ["/users/{actorId}"]).

    Returns
    -------
    dict
        Response from the create_memory_and_wait API call.
    """
    if namespaces is None:
        namespaces = ["/users/{actorId}"]

    strategies = [{
        "customMemoryStrategy": {
            "name": "Semantic",
            "namespaces": namespaces,
            "configuration": {
                "semanticOverride": {
                    "consolidation": {
                        "modelId": model_id,
                        "appendToPrompt": custom_prompt
                    }
                }
            }
        }
    }]

    memory = client.create_memory_and_wait(
        name=name,
        strategies=strategies,
        memory_execution_role_arn=memory_execution_role_arn
    )

    return memory


def list_memories():
    """List all memories."""
    memories = client.list_memories()
    return memories

def add_messages_to_memory(memory_id: str,
                           actor_id: str,
                           session_id: str,
                           messages: list):
    """Add messages to a specific memory."""
    try: 
        client.create_event(
            memory_id=memory_id,
            actor_id=actor_id,
            session_id=session_id,
            messages=messages
        )
    except Exception as e:
        print(f"Error adding messages to memory: {e}")
        raise


def load_conversation_from_memory(memory_id: str,
                                  actor_id: str,
                                  session_id: str,
                                  max_results: int = 5):
    """Load conversation history from a specific memory."""
    try:
        conversation = client.list_events(
            memory_id=memory_id,
            actor_id=actor_id,
            session_id=session_id,
            max_results=max_results
        )
        return conversation
    except Exception as e:
        print(f"Error loading conversation from memory: {e}")
        raise

# The memory_id will be used in following operations
if __name__ == "__main__":
    # Create a new memory
    #memory = create_memory()
    #print(f"Created Memory ID: {memory.get('id')}")

    # List all memories
    memories = list_memories()
    print("List of Memories:")
    for mem in memories:
        print(f"- ID: {mem.get('id')}, ARN: {mem.get('arn')}")


    # create a long-term memory
    CUSTOM_PROMPT = """
    You will be given a text block and a list of summaries you previously generated when available.

    <task>
    You are tasked with analyzing conversations to extract important long-term information about the user.
    You'll be analyzing two sets of data:

    Your goal is to identify and categorize **persistent details** that describe the user and their professional focus.
    Focus on information that helps the system remember who the user is and what matters to them in their business context.

    Specifically, extract and update these key categories when they appear:

    1. Personal Identity
       - User's name or preferred way of being addressed.

    2. Company or Business
       - The name of the user's company, startup, or brand.
       - What industry or sector it belongs to.

    3. Market Analysis Interests
       - Which areas of market analysis or research the user is most interested in
         (e.g., customer segmentation, pricing analysis, competitor tracking, emerging trends, etc.).

    4. Products or Services
       - The main types of products or services the user offers or discusses frequently.
       - Any unique selling points or product categories mentioned.

    5. Competitors
       - Other companies, brands, or benchmarks the user mentions when comparing their own business.
       - Context about how the user perceives these competitors (e.g., trying to match, differentiate, or surpass them).
    </task>
    
    """

    MEMORY_EXECUTION_ROLE_ARN = "arn:aws:iam::444184706474:role/AgentCoreMemoryExecutionRole"
    
    memory = create_long_term_memory(
        name="DeepMarketAgentMemoryV2",
        memory_execution_role_arn=MEMORY_EXECUTION_ROLE_ARN,
        custom_prompt=CUSTOM_PROMPT,
        model_id="anthropic.claude-3-7-sonnet-20250219-v1:0"
    )
    print(memory)

