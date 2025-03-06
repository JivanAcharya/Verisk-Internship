import streamlit as st
import requests
import uuid
from streamlit_chat import message


API_URL = "http://localhost:8000/query"  

# Initialize session state if not present
if "sessions" not in st.session_state:
    st.session_state.sessions = {}
if "current_thread" not in st.session_state:
    st.session_state.current_thread = None


st.sidebar.title("Chat Sessions")
if st.sidebar.button("New Chat"):
    thread_id = str(uuid.uuid4())  # gererating thread_id for the config
    st.session_state.sessions[thread_id] = []
    st.session_state.current_thread = thread_id

# displaying session on the sidebar
for thread_id in st.session_state.sessions.keys():
    if st.sidebar.button(f"Session: {thread_id[:8]}..."):
        st.session_state.current_thread = thread_id

# selecting a session
if st.session_state.current_thread is None:
    st.write("Start a new chat from the sidebar!")
    st.stop()

title_placeholder = st.empty()
title_placeholder.title(f"""University Queries Chatbot
                        \n\nChat Session: {st.session_state.current_thread[:8]}...""")

# put user and bot messages in the chat
for i, chat in enumerate(st.session_state.sessions[st.session_state.current_thread]):
    message(chat["content"], is_user=(chat["role"] == "user"), key=f"chat_message_{i}")

# Input field for user input
user_input = st.text_input("Your Message:", key="input")
if st.button("Send") and user_input:
    user_message = {"role": "user", "content": user_input}
    st.session_state.sessions[st.session_state.current_thread].append(user_message)
    
    # using requests to send post request to the FAST API backend
    try:
        response = requests.post(API_URL, json={"query": user_input, "thread_id":st.session_state.current_thread})
        response_json = response.json()
        print("response JSON: ",response_json)
        bot_response = response_json.get("response", "Error: No response")
    except Exception as e:
        bot_response = f"Error: {str(e)}"
    
    bot_message = {"role": "bot", "content": bot_response}
    st.session_state.sessions[st.session_state.current_thread].append(bot_message)
    
    # rerun page to refresh
    st.rerun()
