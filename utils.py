from google.genai import types
import os
from dotenv import load_dotenv
from google.adk.runners import Runner
from google.adk.sessions import DatabaseSessionService

load_dotenv()

USER_ID = os.getenv("USER_ID")
MODEL_NAME = os.getenv("MODEL_NAME")


# retry_config = types.HttpRetryOptions( 
# attempts=5, # Maximum retry attempts
#  exp_base=7, # Delay multiplier
#  initial_delay=1,
#  http_status_codes=[429, 500, 503, 504], # Retry on these HTTP errors
#  )

async def run_session(
    runner_instance: Runner,
    user_queries: list[str] | str = None,
    session_name: str = "default",
    session_service: DatabaseSessionService = None,
    ):
    print(f"\n ### Session: {session_name}")
    app_name = runner_instance.app_name
    try:
        session = await session_service.create_session(
        app_name=app_name, user_id=USER_ID, session_id=session_name)
    except Exception as e:
         session = await session_service.get_session(
    app_name=app_name, user_id=USER_ID, session_id=session_name )
    if user_queries:
        if type(user_queries) == str:
            user_queries = [user_queries]
        for query in user_queries:
            print(f"\nUser > {query}")
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