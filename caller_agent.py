from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END, MessagesState
import datetime
from tools import book_appointment, get_next_available_appointment, cancel_appointment
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import ToolNode
from langchain_core.messages import HumanMessage
import os
import json

conversations = {}

def get_llm(api_key: str):
    """Initialize and return the LLM with the provided API key"""
    return ChatOpenAI(
        model='gpt-3.5-turbo',
        openai_api_key=api_key
    )

# Edges
def should_continue_caller(state: MessagesState):
    messages = state["messages"]
    last_message = messages[-1]
    if not last_message.tool_calls:
        return "end"
    else:
        return "continue"

# Nodes
def call_caller_model(state: MessagesState):
    state["current_time"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    response = caller_model.invoke(state)
    return {"messages": [response]}

# Tools setup
caller_tools = [book_appointment, get_next_available_appointment, cancel_appointment]
tool_node = ToolNode(caller_tools)

# Prompt setup
caller_pa_prompt = """You are a personal assistant, and need to help the user to book or cancel appointments, you should check the available appointments before booking anything. Be extremely polite, so much so that it is almost rude.
Current time: {current_time}
"""

caller_chat_template = ChatPromptTemplate.from_messages([
    ("system", caller_pa_prompt),
    ("placeholder", "{messages}"),
])

def setup_workflow(llm):
    """Create and return the workflow with the provided LLM"""
    global caller_model  # We need this to be accessible in call_caller_model
    caller_model = caller_chat_template | llm.bind_tools(caller_tools)
    
    # Graph 
    caller_workflow = StateGraph(MessagesState)
    
    # Add Nodes
    caller_workflow.add_node("agent", call_caller_model)
    caller_workflow.add_node("action", tool_node)
    
    # Add Edges
    caller_workflow.add_conditional_edges(
        "agent",
        should_continue_caller,
        {
            "continue": "action",
            "end": END,
        },
    )
    caller_workflow.add_edge("action", "agent")
    
    # Set Entry Point and compile
    caller_workflow.set_entry_point("agent")
    return caller_workflow.compile()

def receive_message_from_caller(message: str, api_key: str, session_id: str):
    """Process a message from the caller using the provided API key"""
    # Initialize conversation for new sessions
    if session_id not in conversations:
        conversations[session_id] = []
    
    llm = get_llm(api_key)
    conversations[session_id].append(HumanMessage(content=message, type="human"))
    
    # Create a new workflow instance with the current LLM
    caller_app = setup_workflow(llm)
    
    state = {
        "messages": conversations[session_id],
    }
    print(state)
    new_state = caller_app.invoke(state)
    conversations[session_id].extend(new_state["messages"][len(conversations[session_id]):])
    
    # Return the conversation history for this session
    return conversations[session_id]

def reset_conversation(session_id: str):
    """Reset the conversation for a specific session"""
    if session_id in conversations:
        conversations[session_id] = []
