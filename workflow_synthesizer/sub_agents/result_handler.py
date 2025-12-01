"""Result Handler Sub-Agent"""

from google.adk.agents import Agent
from ..tools import send_email_notification
from ..config import DEFAULT_MODEL

result_handler = Agent(
    name="result_handler",
    model=DEFAULT_MODEL,
    description="Delivers workflow results via popup or email",
    instruction="""You are the Result Handler. Deliver workflow results via popup or email.

Methods: Popup (default), Email, Both

If workflow specifies email, send automatically.
Otherwise show popup with choice buttons.

Format emails with HTML. Format popups with bullet points.""",
    tools=[send_email_notification],
)
