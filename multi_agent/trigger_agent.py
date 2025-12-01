# Trigger Agent - Sets up and monitors triggers
from core.trigger_manager import TriggerManager
from google.adk.agents import Agent
import os
import datetime

def setup_browser_trigger(trigger_type: str, domains: list = None) -> dict:
    """Set up browser-based triggers."""
    if domains is None:
        domains = ["medium.com"]
    
    trigger_id = f"browser_{trigger_type}_{datetime.datetime.now().timestamp()}"
    return {
        "status": "success",
        "trigger_id": trigger_id,
        "type": trigger_type,
        "domains": domains
    }

def setup_file_trigger(folder_path: str, file_filter: str = "*.*") -> dict:
    """Set up file system triggers."""
    trigger_id = f"file_{datetime.datetime.now().timestamp()}"
    return {
        "status": "success",
        "trigger_id": trigger_id,
        "folder_path": folder_path,
        "file_filter": file_filter
    }

def get_trigger_status(trigger_id: str) -> dict:
    """Get status of a specific trigger."""
    return {"trigger_id": trigger_id, "status": "active", "events_detected": 0}

class TriggerAgent:
    def __init__(self, trigger_manager: TriggerManager):
        self.manager = trigger_manager
        self.triggers = {}
        
        # Google ADK Agent
        self.adk_agent = Agent(
            name="trigger_adk",
            model="gemini-2.0-flash",
            description="Sets up and manages event triggers",
            instruction="You set up triggers for browser events, file changes, and other workflow triggers.",
            tools=[setup_browser_trigger, setup_file_trigger, get_trigger_status]
        )
    
    async def setup_trigger(self, trigger_type: str, conditions: dict) -> str:
        """Set up trigger based on type"""
        config = {"type": trigger_type, "enabled": True}
        
        if trigger_type == "email_compose":
            config.update({"event": "email_compose", "domains": ["mail.google.com"]})
        elif trigger_type == "article_read":
            config.update({"event": "article_read", "domains": conditions.get("domains", ["medium.com"])})
        elif trigger_type == "file_download":
            config.update({
                "type": "file_watcher",
                "folder_path": os.path.expanduser("~/Downloads"),
                "events": ["create"],
                "file_filter": conditions.get("file_filter", "*.pdf")
            })
        
        trigger = self.manager.add_trigger(config)
        trigger_id = f"trigger_{len(self.triggers)}"
        self.triggers[trigger_id] = trigger
        
        return trigger_id
