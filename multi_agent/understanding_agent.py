# Understanding Agent - Parses natural language to workflow using LLM
from google import genai
from google.genai import types
from google.adk.agents import Agent
from config import GEMINI_API_KEY
import json

def parse_natural_language(user_input: str) -> dict:
    """Parse natural language workflow request into structured format."""
    # Simple parsing - in production use LLM
    workflow = {
        "trigger": "article_read",
        "conditions": {"domains": ["medium.com"]},
        "actions": ["summarize"],
        "output": "email",
        "config": {"points": 3}
    }
    
    if "email" in user_input.lower() and "compose" in user_input.lower():
        workflow["trigger"] = "email_compose"
    elif "download" in user_input.lower():
        workflow["trigger"] = "file_download"
    
    if "elaborate" in user_input.lower():
        workflow["actions"] = ["elaborate"]
    elif "suggest" in user_input.lower():
        workflow["actions"] = ["suggest"]
    
    return {"status": "success", "workflow": workflow}

class UnderstandingAgent:
    def __init__(self):
        self.client = genai.Client(api_key=GEMINI_API_KEY)
        self.model = "gemini-2.0-flash-exp"
        
        # Google ADK Agent
        self.adk_agent = Agent(
            name="understanding_adk",
            model="gemini-2.0-flash",
            description="Parses natural language workflow requests",
            instruction="You parse user requests into structured workflows with triggers, actions, and outputs.",
            tools=[parse_natural_language]
        )
    
    async def parse_workflow(self, user_input: str) -> dict:
        """Parse natural language to structured workflow"""
        prompt = f"""Parse this workflow request into JSON:

User request: "{user_input}"

Extract:
1. trigger: (email_compose, article_read, file_download, time_based)
2. conditions: (any filters like domain, file type)
3. actions: list of (summarize, elaborate, suggest, analyze_tone)
4. output: (email, popup, save_file)
5. config: (points, detail_level, recipient)

Return ONLY valid JSON:
{{"trigger": "...", "conditions": {{}}, "actions": [...], "output": "...", "config": {{}}}}"""

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt
        )
        
        import json
        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:-3]
        elif text.startswith("```"):
            text = text[3:-3]
        
        return json.loads(text.strip())
