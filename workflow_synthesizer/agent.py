"""Main Workflow Synthesizer Agent"""

from google.adk.agents import Agent
from google.adk.tools import google_search
from .sub_agents.workflow_planner import workflow_planner
from .sub_agents.workflow_executor import workflow_executor
from .sub_agents.result_handler import result_handler
from .tools import save_workflow_to_file, analyze_trigger_event, send_email_notification
from .config import DEFAULT_MODEL

workflow_synthesizer_agent = Agent(
    name="workflow_synthesizer",
    model=DEFAULT_MODEL,
    description="AI assistant that helps users automate repetitive tasks",
    instruction="""You are the Workflow Synthesizer. Help users automate repetitive tasks.

Steps:
1. Understand automation needs
2. Create workflows with triggers and actions
3. Execute workflows when triggered
4. Deliver results via popup or email

Be concise and action-oriented.""",
    tools=[
        google_search,
        save_workflow_to_file,
        analyze_trigger_event,
        send_email_notification,
    ],
)
