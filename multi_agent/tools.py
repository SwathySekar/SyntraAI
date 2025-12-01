# Tools for Hierarchical Multi-Agent System
from tools.summarizer import LLMProcessor
import json

def parse_natural_language(user_input: str) -> dict:
    """Parse natural language workflow request into structured format."""
    # Simple parsing logic - can be enhanced with LLM
    workflow = {
        "trigger_type": "article_read",
        "conditions": {"domains": ["medium.com"]},
        "actions": ["process_dynamically"],
        "output_method": "popup",
        "config": {"dynamic": True}
    }
    
    if "email" in user_input.lower() and "compose" in user_input.lower():
        workflow["trigger_type"] = "email_compose"
    elif "download" in user_input.lower() or "file" in user_input.lower():
        workflow["trigger_type"] = "file_download"
    
    if "email me" in user_input.lower():
        workflow["output_method"] = "email"
    
    return {"status": "success", "workflow": workflow}

def setup_triggers(trigger_type: str, conditions: dict = None) -> dict:
    """Set up triggers based on workflow requirements."""
    if conditions is None:
        conditions = {}
    
    trigger_config = {
        "type": trigger_type,
        "enabled": True,
        "conditions": conditions
    }
    
    if trigger_type == "file_download":
        trigger_config.update({
            "folder_path": "~/Downloads",
            "events": ["create"],
            "file_filter": "*"
        })
    elif trigger_type == "email_compose":
        trigger_config.update({
            "domains": ["mail.google.com"],
            "event": "compose"
        })
    elif trigger_type == "article_read":
        trigger_config.update({
            "domains": conditions.get("domains", ["medium.com"]),
            "event": "article_open"
        })
    
    return {"status": "success", "trigger_id": f"trigger_{trigger_type}", "config": trigger_config}

def process_with_dynamic_query(content: str, user_query: str) -> dict:
    """Process content dynamically based on user query using LLM."""
    try:
        llm_processor = LLMProcessor()
        result = llm_processor.process_with_query(content, user_query)
        return {
            "action": "dynamic_processing",
            "result": result.get('response', 'No response available'),
            "success": result.get('success', False),
            "user_query": user_query
        }
    except Exception as e:
        return {
            "action": "dynamic_processing", 
            "result": f"Processing failed: {str(e)}",
            "success": False,
            "user_query": user_query
        }

def send_email_delivery(results: str, recipient: str = "swathyecengg@gmail.com") -> dict:
    """Send results via email delivery."""
    try:
        # Import here to avoid circular imports
        from workflow_synthesizer.tools import send_email_notification
        
        subject = "Syntra: Workflow Result"
        body = f"<div style='font-family: Arial, sans-serif;'>{results}</div>"
        
        result = send_email_notification(recipient, subject, body)
        return {"status": "success", "method": "email", "message": result}
    except Exception as e:
        return {"status": "failed", "method": "email", "error": str(e)}

def extract_event_content(event_data: dict) -> str:
    """Extract content from different event types."""
    # File events
    if 'file_path' in event_data or 'file_name' in event_data:
        file_name = event_data.get('file_name', 'Unknown file')
        file_path = event_data.get('file_path', '')
        return f"File: {file_name}\nPath: {file_path}"
    
    # Email events
    elif 'email_subject' in event_data or 'email_body' in event_data:
        subject = event_data.get('email_subject', '')
        body = event_data.get('email_body', '')
        return f"Subject: {subject}\nBody: {body}" if body else f"Subject: {subject}"
    
    # Article events  
    elif 'title' in event_data and 'content' in event_data:
        title = event_data.get('title', '')
        content = event_data.get('content', '')
        return f"Title: {title}\nContent: {content[:1000]}..."
    
    return event_data.get('content', 'No content available')