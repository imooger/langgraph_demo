
import os

# with open(".env", "r") as f:
#     for line in f:
#         key, value = line.split("=")
#         os.environ[key] = value.strip()

import dotenv
dotenv.load_dotenv()

import streamlit as st
from caller_agent import receive_message_from_caller, reset_conversation
from tools import APPOINTMENTS
from langchain_core.messages import HumanMessage
import langsmith
import uuid

langsmith.debug = True                                                   

st.set_page_config(layout="wide")           

if "messages" not in st.session_state:
    st.session_state.messages = []

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

def submit_message():
    if not st.session_state.get("openai_api_key"):
        st.error("Please enter your OpenAI API key in the sidebar!")
        return
    
    # Use Streamlit's session ID as the conversation ID
    session_id = st.session_state.session_id
    
    # Pass the session_id to receive_message_from_caller
    conversation_history = receive_message_from_caller(
        st.session_state["message"], 
        st.session_state["openai_api_key"],
        session_id
    )
    
    # Update the session state with the new conversation history
    st.session_state.messages = conversation_history

def reset_chat():
    """Reset the chat conversation"""
    session_id = st.session_state.session_id
    reset_conversation(session_id)
    st.session_state.messages = []





# Sidebar
with st.sidebar:
    with st.popover("API KEYS", icon="🔑"):
        openai_api_key = st.text_input(
            "OpenAI API Key",
            type="password",
            key="openai_api_key",
            help="Get your API key from https://platform.openai.com/account/api-keys"
        )
        if not openai_api_key:
            st.warning("Please enter your OpenAI API key!", icon="⚠️")

    st.button("Reset Conversation", on_click=reset_chat, type="primary")



col1, col2 = st.columns(2)

col1, col2 = st.columns(2)

with col1:
    st.subheader("Appointment Manager")

    # Display chat messages from history
    for message in st.session_state.messages:
        if type(message) == HumanMessage:
            with st.chat_message("user"):
                st.write(message.content)
        else:
            with st.chat_message("assistant"):
                st.write(message.content)
    
    message = st.chat_input("Type message here", on_submit=submit_message, key="message")

with col2:
    st.header("Appointments")
    st.write(APPOINTMENTS)
