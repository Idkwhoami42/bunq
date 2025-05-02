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
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("What would you like to know about financial planning?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Prepare the request to the FastAPI server
    request_data = {
        "conversation_id": st.session_state.conversation_id,
        "location": {
            "latitude": 37.774929,
            "longitude": -122.419418
        },
        
        "messages": st.session_state.messages
    }
    
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
            # If we got a pot creation response
            assistant_message = response_data["message"]
            if "pot" in response_data:
                st.json(response_data["pot"])
        else:
            # Regular chat response
            assistant_message = response_data
        
        # Add assistant message to chat history
        st.session_state.messages.append({"role": "assistant", "content": assistant_message})
        
        # Display assistant message
        with st.chat_message("assistant"):
            st.markdown(assistant_message)
            
    except requests.exceptions.RequestException as e:
        st.error(f"Error connecting to the server: {str(e)}")
        st.info("Make sure the FastAPI server is running on http://localhost:8000")

# Add a clear chat button
if st.button("Clear Chat"):
    st.session_state.messages = []
    st.rerun() 