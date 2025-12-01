"""Custom tools for Workflow Synthesizer Agent"""

import os
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from .config import GMAIL_USER, GMAIL_APP_PASSWORD, GMAIL_DISPLAY_NAME


# Tool functions for ADK
def save_workflow_to_file(workflow_data: dict, filename: str) -> str:
    """Saves a workflow configuration to a JSON file in the workflows directory."""
    workflows_dir = os.path.expanduser("~/Documents/WorkFLowSynthesizer/workflows")
    os.makedirs(workflows_dir, exist_ok=True)
    filepath = os.path.join(workflows_dir, f"{filename}.json")
    with open(filepath, 'w') as f:
        json.dump(workflow_data, f, indent=2)
    return f"Workflow saved to {filepath}"


def analyze_trigger_event(event_data: dict) -> dict:
    """Analyzes a trigger event (file, email, article) and extracts structured information."""
    event_type = event_data.get("event_type", "unknown")
    
    if event_type == "file_download":
        return {
            "type": "file",
            "filename": event_data.get("filename", "unknown"),
            "size": event_data.get("size", 0),
            "path": event_data.get("path", ""),
            "timestamp": datetime.now().isoformat(),
        }
    elif event_type == "article_read":
        return {
            "type": "article",
            "title": event_data.get("title", "Untitled"),
            "content": event_data.get("content", "")[:500],
            "url": event_data.get("url", ""),
            "timestamp": datetime.now().isoformat(),
        }
    elif event_type == "email_compose":
        return {
            "type": "email",
            "subject": event_data.get("subject", "No subject"),
            "body": event_data.get("body", ""),
            "recipient": event_data.get("recipient", ""),
            "timestamp": datetime.now().isoformat(),
        }
    return {"type": "unknown", "raw": event_data}


def send_email_notification(recipient: str, subject: str, body: str) -> str:
    """Sends an email notification with workflow results via Gmail SMTP."""
    try:
        msg = MIMEMultipart('alternative')
        msg['From'] = f"{GMAIL_DISPLAY_NAME} <{GMAIL_USER}>"
        msg['To'] = recipient
        msg['Subject'] = subject
        
        html_body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #4285f4;">Workflow Result</h2>
                    <div style="background: #f5f5f5; padding: 15px; border-radius: 5px;">
                        {body}
                    </div>
                    <p style="color: #666; font-size: 12px; margin-top: 20px;">
                        Sent by Workflow Synthesizer
                    </p>
                </div>
            </body>
        </html>
        """
        
        msg.attach(MIMEText(html_body, 'html'))
        
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
            server.send_message(msg)
        
        return f"Email sent successfully to {recipient}"
    except Exception as e:
        return f"Failed to send email: {str(e)}"
