import uuid
import os
from dotenv import load_dotenv
from google.adk.agents import Agent, SequentialAgent, ParallelAgent, LoopAgent, LlmAgent 
from google.adk.runners import InMemoryRunner, Runner
from google.adk.tools import AgentTool, FunctionTool
from google.genai import types
from google.adk.agents.callback_context import CallbackContext
from google.adk.sessions import DatabaseSessionService
from google.adk.agents import Agent
from google.adk.tools import ToolContext, FunctionTool
from google.adk.sessions import InMemorySessionService
from google.adk.apps import App

from tools import  load_csv_to_sqlite_file, getLoanMetadata, setCustomerContext
from utils import  run_session

load_dotenv()

DB_URL = os.getenv("DB_URL")
SESSION_ID = str(uuid.uuid4())

lead_agent = Agent(
    model='gemini-2.5-flash',
    name='lead_agent',
    description='A sales agent for loan products.',
    instruction='''You are a Loan Sales Agent. 
    Your primary role is to provide information about various loan products based on the content of
    the provided PDF document. Use the available tool getLoanMetadata to extract information and answer
    user queries. If the information is not in the PDF, state that you cannot find it.''',
    tools=[getLoanMetadata],
    output_key="loaninfo",
    before_agent_callback = load_csv_to_sqlite_file )

orchestrator = Agent(
    model="gemini-2.5-flash",
    name='BankBuddyAgent',
    description='A loan service agent that answers user questions about loan products and assists with applications.',
    instruction="""You are a helpful loan service agent. Assist users with their inquiries about loan products and guide them through the application process.
    1. Prompt user for customer ID. Use 'setCustomerContext' tool to fetch customer demographic data using customer ID provided by user and greet the customer using name
    2. use 'lead-agent' tool to fetch loan information as requersted by customer
    """,
    tools=[setCustomerContext],
    sub_agents = [lead_agent]
)

bankApp = App(
    name='hello_world_app',
    root_agent=orchestrator
)

async def get_bankbuddy_response(user_prompt: str, user_id: str) -> str:
    # runner = InMemoryRunner(app=bankApp)
    # session_id = f"{user_id}-{str(uuid.uuid4())}"

    # response = runner.run_debug(
    #     user_prompt,
    # )

    session_service = DatabaseSessionService(db_url=DB_URL)
    runner = Runner(app=bankApp, session_service=session_service)
    
    return await run_session(
        runner, user_queries=user_prompt, session_name=SESSION_ID, session_service=session_service)
