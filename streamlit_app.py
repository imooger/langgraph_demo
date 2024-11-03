
import os

# with open(".env", "r") as f:
#     for line in f:
#         key, value = line.split("=")
#         os.environ[key] = value.strip()

import dotenv
dotenv.load_dotenv()

import streamlit as st
from caller_agent import CONVERSATION, receive_message_from_caller
from tools import APPOINTMENTS
from langchain_core.messages import HumanMessage
import langsmith

langsmith.debug = True                                                   

st.set_page_config(layout="wide")           

def submit_message():
    if not st.session_state.get("openai_api_key"):
        st.error("Please enter your OpenAI API key in the sidebar!")
        return
    # Pass the API key to receive_message_from_caller
    receive_message_from_caller(st.session_state["message"], st.session_state["openai_api_key"])

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


col1, col2 = st.columns(2)

with col1:
    st.subheader("Appointment Manager")

    for message in CONVERSATION:
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
