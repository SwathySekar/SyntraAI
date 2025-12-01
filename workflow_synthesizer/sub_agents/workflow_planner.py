"""Workflow Planner Sub-Agent"""

from google.adk.agents import Agent
from google.adk.tools import google_search
from ..config import DEFAULT_MODEL

workflow_planner = Agent(
    name="workflow_planner",
    model=DEFAULT_MODEL,
    description="Analyzes user requests and creates structured workflows",
    instruction="""You are the Workflow Planner. Analyze user requests and create structured workflows.

Identify:
1. Trigger: file download, email compose, article read
2. Actions: summarize, analyze, notify
3. Output: popup, email, both

Extract email addresses from natural language.

Return format:
Trigger: [type]
Actions: [list]
Output: [method]
Email: [address if specified]""",
    tools=[google_search],
)
