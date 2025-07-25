import os
import uuid
from dotenv import load_dotenv
from langchain_community.chat_message_histories import FileChatMessageHistory
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langchain_core.chat_history import InMemoryChatMessageHistory
from langgraph.graph import START, MessagesState, StateGraph

# Load API key from .env
load_dotenv()

# In-memory store of chat sessions
chats_by_session_id = {}

# Initialize model
model = ChatOpenAI(model="gpt-4o", temperature=0)

# Session-based chat memory
def get_chat_history(session_id: str) -> FileChatMessageHistory:
    history_dir = "chat_histories"
    os.makedirs(history_dir, exist_ok=True)
    return FileChatMessageHistory(os.path.join(history_dir, f"{session_id}.json"))

# LangGraph node to handle model calls
def call_model(state: MessagesState, config: RunnableConfig) -> dict:
    session_id = config.get("configurable", {}).get("session_id")
    if not session_id:
        raise ValueError("Missing session_id in config['configurable']")

    chat_history = get_chat_history(session_id)

    # Add system instruction to guide the model
    system_message = SystemMessage(content="Here is the conversation history. Use it to answer the user's current question.")

    # Compose full message history with system message
    messages = [system_message] + list(chat_history.messages) + state["messages"]

    # Call the model
    ai_message = model.invoke(messages)

    # Store current messages + model reply
    chat_history.add_messages(state["messages"] + [ai_message])

    return {"messages": ai_message}

# LangGraph definition
builder = StateGraph(state_schema=MessagesState)
builder.add_node("model", call_model)
builder.set_entry_point("model")
graph = builder.compile()

# Create a session ID (e.g., based on user email)
def get_or_create_session_id(user_email: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, user_email))
