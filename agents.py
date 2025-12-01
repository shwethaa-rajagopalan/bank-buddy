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
from google.adk.apps.app import EventsCompactionConfig
import streamlit as st
from tools import   getLoanMetadata, setCustomerContext, getAllLoanApplications, getCustomerData, getLoanApplication, saveLoanApplication
from utils import  run_session, set_agent_state

load_dotenv()

DB_URL = 'sqlite:///customer_data.db'
SESSION_ID = str(st.session_state.to_dict()['customer_id']) + str(uuid.uuid4())
# print(f"Session ID: {SESSION_ID}")
print("Customer id:", st.session_state.to_dict()['customer_id'] )

lead_agent = Agent(
    model='gemini-2.5-flash',
    name='lead_agent',
    description='A sales agent for loan products.',
    instruction='''You are a Loan Sales Agent. 
    Your primary role is to provide information about various loan products based on the content of
    the provided PDF document. Use the available tool getLoanMetadata to extract information and answer
    user queries. If the information is not in the PDF, state that you cannot find it.''',
    tools=[getLoanMetadata],
    output_key="loaninfo")

application_agent = Agent(
    model='gemini-2.5-flash',
    name='application_agent',
    description='An agent that assists users with loan applications.',
    instruction='''You are a Loan Application Agent.
    Customer ID: {customer_id}.
    Your primary role is to assist users in filling out loan applications .
    To fetch loan application data, use the getLoanApplication and getAllLoanApplications tools depending on user query.
    To save loan application data, use the saveLoanApplication tool. The tool accepts customer_id, 
    loan type in ['mortgage','education', 'personal','car'], loan_amount and ID of any identification proof. Ask the user if any of these are not available.
    Before submitting the information, confirm all details with the user.
    The tool saveLoanApplication accepts a dictionary with keys: customer_id, loan_type, loan_amount, identification.
    Return the saved application ID to the user after saving.
    '''.format(customer_id=st.session_state.get("customer_id")),
    tools=[getLoanApplication, getAllLoanApplications, saveLoanApplication]
)


orchestrator = Agent(
    model="gemini-2.5-flash",
    name='BankBuddyAgent',
    description='A loan service agent that answers user questions about loan products and assists with applications.',
    instruction="""You are a helpful loan service agent. Assist users with their inquiries about loan products and guide them through the application process.
    Customer data: First name {first_name}, Last name {last_name}, Customer ID {customer_id}.

    1. Always Greet the customer using their first name
    2. use 'lead-agent' tool to fetch loan information as requested by customer
    3. use 'application-agent' tool to assist with loan applications as requested by customer
    4. always be polite and professional
    5. if you are unable to help with a request, politely inform the user that you cannot assist with that request.
    Format your responses as bullet points where applicable to ensure readability.
    """.format(first_name=st.session_state.get("first_name"), last_name=st.session_state.get("last_name"), customer_id=st.session_state.get("customer_id")),
    tools=[setCustomerContext],
    sub_agents=[lead_agent, application_agent],
    before_agent_callback=set_agent_state
)

bankApp = App(
    name='hello_world_app',
    root_agent=orchestrator,
    events_compaction_config=EventsCompactionConfig(
        compaction_interval=3,  
        overlap_size=1         
    ),
)

async def get_bankbuddy_response(user_prompt: str) -> str:
    # runner = InMemoryRunner(app=bankApp)
    # session_id = f"{user_id}-{str(uuid.uuid4())}"

    # response = runner.run_debug(
    #     user_prompt,
    # )

    session_service = DatabaseSessionService(db_url=DB_URL)
    runner = Runner(app=bankApp, session_service=session_service)
    
    return await run_session(
        runner, user_queries=user_prompt, session_name=SESSION_ID, session_service=session_service)
