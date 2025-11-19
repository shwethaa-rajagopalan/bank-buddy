from google.adk.agents import LlmAgent
from config.settings import MODEL_GEMINI, APP_NAME_FOR_ADK, USER_ID

def create_orchestrator_agent():
    """Creates and returns an orchestrator LlmAgent configured for the loan-easy application."""
    orchestrator_agent = LlmAgent(
    model='gemini-2.5-flash',
    name='orchestrator_agent',
    description='A sales agent for loan products.',
    instruction='Engage with users to understand their loan needs and recommend suitable loan products.',
)

    return orchestrator_agent