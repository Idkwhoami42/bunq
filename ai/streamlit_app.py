import streamlit as st
import requests
import json
from typing import List, Dict, Any

# Configure the page
st.set_page_config(
    page_title="Financial Planner Chat",
    page_icon="💰",
    layout="wide"
)

# Initialize session state for messages if it doesn't exist
if "messages" not in st.session_state:
    st.session_state.messages = []
if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = "demo_conversation"

# Title and description
st.title("💰 Financial Planner Chat")
st.markdown("""
This is a demo of the Financial Planner AI assistant. You can chat with it to create and manage financial pots.
""")

# Chat interface
for idx, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        col1, col2 = st.columns([10, 1])
        with col1:
            st.markdown(message["content"])
            if message["role"] == "assistant":
                if "pot" in message and message["pot"]:
                    st.json(message["pot"])
                else:
                    st.info("Pot not created yet")
        with col2:
            if st.button("🗑️", key=f"delete_{idx}"):
                st.session_state.messages.pop(idx)
                st.rerun()

# Chat input
if prompt := st.chat_input("What would you like to know about financial planning?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
        
         # replace user with 'sagar' in the messages
    send_messages = [{"role": "sagar", "content": message["content"]} for message in st.session_state.messages]
    
    # Get the latest pot from assistant messages
    latest_pot = None
    for message in reversed(st.session_state.messages):
        if message["role"] == "assistant" and message.get("pot"):
            latest_pot = message["pot"]
            break
    
    # Prepare the request to the FastAPI server
    request_data = {
        "conversation_id": st.session_state.conversation_id,
        "location": {
            "latitude": 37.774929,
            "longitude": -122.419418
        },
        "participants": ["Manu", "Ege", "Sagar"],
        "messages": send_messages
    }
    
    # Only add pot if it exists
    if latest_pot is not None:
        request_data["pot"] = latest_pot

    # Make the request to the FastAPI server
    try:
        response = requests.post(
            "http://localhost:8000/chat",
            json=request_data
        )
        response.raise_for_status()
        
        # Get the response
        response_data = response.json()
        
        # Handle the response
        if isinstance(response_data, dict) and "message" in response_data:
            # Add assistant message to chat history with pot information
            assistant_message = {
                "role": "assistant",
                "content": response_data["message"],
                "pot": response_data.get("pot")
            }
            st.session_state.messages.append(assistant_message)
        else:
            # Regular chat response
            st.session_state.messages.append({
                "role": "assistant",
                "content": response_data,
                "pot": None
            })
        
        # Rerun to display the new messages
        st.rerun()
            
    except requests.exceptions.RequestException as e:
        st.error(f"Error connecting to the server: {str(e)}")
        st.info("Make sure the FastAPI server is running on http://localhost:8000")

# Add a clear chat button
if st.button("Clear Chat"):
    st.session_state.messages = []
    st.rerun() 