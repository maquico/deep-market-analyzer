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
