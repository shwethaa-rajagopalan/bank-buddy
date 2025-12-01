import streamlit as st
import requests
import json
import asyncio


def chat_page():

    st.set_page_config(page_title="Lendly", layout="centered")
    st.title("Lendly Agent")
    if st.button("Logout"):
        st.session_state.update({"logged_in": False})
        st.switch_page("app.py")

    if "messages" not in st.session_state:
        st.session_state.messages = []
        st.session_state.messages.append({"role": "assistant", "content": "Hello! I am your Lendly. I can guide you on loans and also help you with your applications. What can I do for you today?"})

   
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask me about loans...", key="main_chat_input"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Lendly is thinking ..."):

                full_response = get_adk_response(prompt)
                st.markdown(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})

def get_adk_response(user_prompt):
    from agents import get_bankbuddy_response
    try:
        resp = asyncio.run(get_bankbuddy_response(user_prompt))
        return resp
        # return get_bankbuddy_response(user_prompt, "admin")
    except requests.exceptions.RequestException as e:
        return f"I couldnt process this. Please try again in some time?"
    

chat_page()