from google.genai import types
import os
from dotenv import load_dotenv
from google.adk.runners import Runner
from google.adk.sessions import DatabaseSessionService
from google.adk.agents.callback_context import CallbackContext
import streamlit as st
load_dotenv()

USER_ID = st.session_state.get("customer_id")
# retry_config = types.HttpRetryOptions( 
# attempts=5, # Maximum retry attempts
#  exp_base=7, # Delay multiplier
#  initial_delay=1,
#  http_status_codes=[429, 500, 503, 504], # Retry on these HTTP errors
#  )

def set_agent_state (callback_context: CallbackContext):
    for key, value in st.session_state.items():
        callback_context.state[key] = value
    # print(f"Callback Context State: {callback_context.state.to_dict()}")

async def run_session(
    runner_instance: Runner,
    user_queries: list[str] | str = None,
    session_name: str = "default",
    session_service: DatabaseSessionService = None,
    ):
    app_name = runner_instance.app_name
    try:
        session = await session_service.create_session(
        app_name=app_name, user_id=USER_ID, session_id=session_name)
        print(f"Created new session: {session.state.to_dict()}")
    except Exception as e:
         session = await session_service.get_session(
    app_name=app_name, user_id=USER_ID, session_id=session_name )
    if user_queries:
        if type(user_queries) == str:
            user_queries = [user_queries]
        for query in user_queries:
            query = types.Content(role="user", parts=[types.Part(text=query)])
            async for event in runner_instance.run_async(
                user_id=USER_ID, session_id=session.id, new_message=query):
                if event.content and event.content.parts:
                    if (
                    event.content.parts[0].text != "None"
                    and event.content.parts[0].text):
                        return event.content.parts[0].text
    else:
        print("No queries!")