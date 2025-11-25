import streamlit as st
import requests
import json
import asyncio


def chat_page():

    st.set_page_config(page_title="ADK Chatbot", layout="centered")
    st.title("🤖 Google ADK Agent Chat")

    if "messages" not in st.session_state:
        st.session_state.messages = []
        st.session_state.messages.append({"role": "assistant", "content": "Hello! I am your ADK-powered assistant. How can I help you today?"})

   
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask your ADK agent...", key="main_chat_input"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Agent is thinking..."):

                full_response = get_adk_response(prompt)
                st.markdown(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})

def get_adk_response(user_prompt):
    from agents import get_bankbuddy_response
    try:
        resp = asyncio.run(get_bankbuddy_response(user_prompt, "admin"))
        print("Response from ADK Agent:", resp)
        return resp
        # return get_bankbuddy_response(user_prompt, "admin")
    except requests.exceptions.RequestException as e:
        return f"Error communicating with ADK Agent API: {e}. Is the agent server running?"



if __name__ == "__main__":
    chat_page()