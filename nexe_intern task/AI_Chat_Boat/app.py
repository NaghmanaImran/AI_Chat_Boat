import streamlit as st
import json
import requests

# Ollama endpoint configuration
OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "gpt-oss:120b-cloud"

# Page config
st.set_page_config(
    page_title="AI Chatbot",
    page_icon="🤖",
    layout="centered"
)

st.title("🤖 AI Chatbot")
st.caption("Powered by Ollama")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


def send_message(messages):
    payload = {
        "model": MODEL,
        "messages": messages,
    }
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=60)
    except requests.exceptions.RequestException as exc:
        return f"Error: Failed to connect to Ollama — {exc}"

    if response.status_code != 200:
        return f"Error: Ollama returned status {response.status_code}"

    full_response = ""
    for line in response.text.strip().split("\n"):
        if line.strip():
            try:
                data = json.loads(line)
                if "message" in data:
                    full_response += data["message"].get("content", "")
            except json.JSONDecodeError:
                continue

    return full_response if full_response else "Error: No response received"


# Chat input
if prompt := st.chat_input("Type your message here..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get AI response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = send_message(st.session_state.messages)
        st.markdown(response)

    # Save assistant response
    st.session_state.messages.append({"role": "assistant", "content": response})
