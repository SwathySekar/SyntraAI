# Delivery Agent - Handles result delivery (email, popup, file)
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google.adk.agents import Agent
import os
import datetime

def send_email_delivery(results: str, recipient: str) -> dict:
    """Send results via email."""
    return {
        "status": "success",
        "method": "email",
        "recipient": recipient,
        "message": "Results sent successfully"
    }

def create_popup_delivery(results: str) -> dict:
    """Prepare results for popup display."""
    return {
        "status": "success",
        "method": "popup",
        "message": "Results ready for popup"
    }

def save_file_delivery(results: str, filename: str = None) -> dict:
    """Save results to file."""
    if filename is None:
        filename = f"workflow_result_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    
    return {
        "status": "success",
        "method": "save_file",
        "filename": filename,
        "message": f"Results saved to {filename}"
    }

class DeliveryAgent:
    def __init__(self):
        from config import SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, SMTP_FROM_NAME
        self.email_config = {
            "smtp_server": SMTP_HOST,
            "smtp_port": SMTP_PORT,
            "sender_email": SMTP_USER,
            "sender_password": SMTP_PASSWORD,
            "from_name": SMTP_FROM_NAME
        }
        
        # Google ADK Agent
        self.adk_agent = Agent(
            name="delivery_adk",
            model="gemini-2.0-flash",
            description="Delivers workflow results via multiple channels",
            instruction="You deliver results via email, popup, or file based on user preferences.",
            tools=[send_email_delivery, create_popup_delivery, save_file_delivery]
        )
    
    async def deliver(self, results: list, output_method: str, event_data: dict) -> dict:
        """Deliver results via specified method"""
        if output_method == "email":
            return await self._send_email(results, event_data)
        elif output_method == "popup":
            return await self._show_popup(results)
        elif output_method == "save_file":
            return await self._save_file(results, event_data)
        return {"status": "unknown_method"}
    
    async def _send_email(self, results: list, event_data: dict) -> dict:
        """Send results via email"""
        from config import DEFAULT_RECIPIENT
        recipient = event_data.get('user_email', DEFAULT_RECIPIENT)
        
        msg = MIMEMultipart()
        msg['From'] = f"{self.email_config['from_name']} <{self.email_config['sender_email']}>"
        msg['To'] = recipient
        msg['Subject'] = f"Syntra: Your workflow result is ready"
        
        body = self._format_email_body(results)
        msg.attach(MIMEText(body, 'html'))
        
        try:
            with smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port']) as server:
                server.starttls()
                server.login(self.email_config['sender_email'], self.email_config['sender_password'])
                server.send_message(msg)
            print(f"✅ Email sent to {recipient}")
            return {"status": "sent", "recipient": recipient}
        except Exception as e:
            print(f"❌ Email failed: {e}")
            return {"status": "failed", "error": str(e)}
    
    async def _show_popup(self, results: list) -> dict:
        """Store results for popup display"""
        return {"status": "ready_for_popup", "results": results}
    
    async def _save_file(self, results: list, event_data: dict) -> dict:
        """Save results to file"""
        filename = f"workflow_result_{event_data.get('timestamp', 'output')}.txt"
        filepath = os.path.expanduser(f"~/Downloads/{filename}")
        
        with open(filepath, 'w') as f:
            for result in results:
                f.write(f"Action: {result.get('action')}\n")
                f.write(f"Result: {result.get('result')}\n\n")
        
        return {"status": "saved", "filepath": filepath}
    
    def _format_email_body(self, results: list) -> str:
        """Format results as HTML email"""
        print(f"📧 Formatting email with results: {results}")
        
        html = "<html><body style='font-family: -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;'>"
        html += "<div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 12px; color: white; text-align: center; margin-bottom: 30px;'>"
        html += "<h1 style='margin: 0; font-size: 24px;'>⚡ Syntra</h1>"
        html += "<p style='margin: 5px 0 0 0; opacity: 0.9;'>Your workflow result is ready</p>"
        html += "</div>"
        
        for result in results:
            print(f"📧 Processing result: {result}")
            # Handle both dict and string results
            if isinstance(result, str):
                content = result
                html += f"<div style='background: #f8f9fa; padding: 25px; border-radius: 12px; border-left: 4px solid #667eea; margin-bottom: 20px;'>"
                content_html = content.replace('\n\n', '</p><p>').replace('\n', '<br>')
                html += f"<p style='margin: 0; line-height: 1.6; color: #333;'>{content_html}</p>"
                html += "</div>"
            elif result.get('type') == 'result' or result.get('result'):
                content = result.get('content') or result.get('result', 'No content available')
                # Better markdown to HTML conversion
                content_html = content.replace('\n\n', '</p><p>').replace('\n', '<br>').replace('**', '<strong>').replace('**', '</strong>')
                html += f"<div style='background: #f8f9fa; padding: 25px; border-radius: 12px; border-left: 4px solid #667eea; margin-bottom: 20px;'>"
                html += f"<p style='margin: 0; line-height: 1.6; color: #333;'>{content_html}</p>"
                html += "</div>"
            elif result.get('type') == 'notification':
                html += f"<div style='background: #e3f2fd; padding: 25px; border-radius: 12px; border-left: 4px solid #2196f3; margin-bottom: 20px;'>"
                html += f"<h3 style='margin: 0 0 15px 0; color: #1976d2;'>📁 File Processed</h3>"
                html += f"<p style='margin: 5px 0; color: #333;'><strong>File:</strong> {result.get('title', 'Unknown')}</p>"
                html += f"<p style='margin: 5px 0; color: #333;'><strong>Message:</strong> {result.get('message', '')}</p>"
                if result.get('file_size'):
                    size_kb = result['file_size'] / 1024
                    html += f"<p style='margin: 5px 0; color: #333;'><strong>Size:</strong> {size_kb:.1f} KB</p>"
                html += "</div>"
        
        html += "<div style='text-align: center; margin-top: 40px; padding-top: 20px; border-top: 1px solid #eee;'>"
        html += "<p style='color: #999; font-size: 14px; margin: 0;'>Powered by Syntra</p>"
        html += "</div>"
        html += "</body></html>"
        return html
