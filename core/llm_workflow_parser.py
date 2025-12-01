# Simple LLM-Based Workflow Parser using existing Gemini setup
import json
import re
import requests
from config import GEMINI_API_KEY

class LLMWorkflowParser:
    def __init__(self):
        self.api_key = GEMINI_API_KEY
        self.api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={self.api_key}"
    
    def parse_workflow_intent(self, user_query: str) -> dict:
        """Parse user query to extract workflow intent using LLM"""
        
        # Use existing Gemini client through summarizer
        prompt = f"""Analyze this workflow request and return JSON:

User Query: "{user_query}"

Extract:
1. trigger_type: file_download, email_compose, email_read, article_read, or browser_event
2. conditions: file extensions, domains, keywords
3. actions: summarize, analyze_tone, notify_file, extract_text
4. output_method: email, popup, or save_file
5. confidence: 0.0 to 1.0

Return only JSON:
{{"trigger_type": "...", "conditions": {{}}, "actions": [...], "output_method": "...", "confidence": 0.95}}"""

        try:
            # Use REST API like summarizer tool
            payload = {"contents": [{"parts": [{"text": prompt}]}]}
            response = requests.post(self.api_url, json=payload, timeout=30)
            
            if response.status_code != 200:
                print(f"Gemini API Error: {response.status_code}")
                return self._fallback_parse(user_query)
            
            result = response.json()
            if 'candidates' in result and len(result['candidates']) > 0:
                text = result['candidates'][0]['content']['parts'][0]['text'].strip()
                
                # Parse JSON response
                if text.startswith("```json"):
                    text = text[7:-3]
                elif text.startswith("```"):
                    text = text[3:-3]
                
                return json.loads(text.strip())
            else:
                return self._fallback_parse(user_query)
            
        except Exception as e:
            print(f"LLM parsing failed: {e}")
            return self._fallback_parse(user_query)
    
    def _fallback_parse(self, query: str) -> dict:
        """Simple fallback parsing"""
        q = query.lower()
        
        # Detect trigger type
        if any(word in q for word in ['download', 'file', 'pdf']):
            trigger_type = "file_download"
        elif any(word in q for word in ['compose', 'composing', 'write', 'writing email']):
            trigger_type = "email_compose"
        elif any(word in q for word in ['open', 'read', 'reading email', 'receive']):
            trigger_type = "email_read"
        elif any(word in q for word in ['article', 'medium']):
            trigger_type = "article_read"
        else:
            trigger_type = "browser_event"
        
        # Detect actions
        actions = []
        if any(word in q for word in ['summarize', 'summary', 'key points']):
            actions.append('summarize')
        if any(word in q for word in ['analyze', 'tone', 'feedback']):
            actions.append('analyze_tone')
        if any(word in q for word in ['notify', 'alert', 'tell me']):
            actions.append('notify_file')
        
        if not actions:
            actions = ['summarize'] if trigger_type == "article_read" else ['notify_file']
        
        # Detect output method
        output_method = "email" if "email" in q else "popup"
        
        return {
            "trigger_type": trigger_type,
            "conditions": {},
            "actions": actions,
            "output_method": output_method,
            "confidence": 0.7
        }
    
    def create_trigger_config(self, workflow_intent: dict) -> dict:
        """Convert workflow intent to trigger configuration"""
        trigger_type = workflow_intent["trigger_type"]
        conditions = workflow_intent.get("conditions", {})
        
        if trigger_type == "file_download":
            return {
                "type": "file_watcher",
                "folder_path": "~/Downloads",
                "events": ["create"],
                "file_filter": "*.pdf" if "pdf" in str(conditions) else "*.*",
                "enabled": True
            }
        elif trigger_type == "email_compose":
            return {
                "type": "browser_event",
                "event": "email_compose",
                "domains": ["mail.google.com"],
                "enabled": True
            }
        elif trigger_type == "email_read":
            return {
                "type": "browser_event",
                "event": "email_read",
                "domains": ["mail.google.com"],
                "enabled": True
            }
        elif trigger_type == "article_read":
            return {
                "type": "browser_event", 
                "event": "article_read",
                "domains": ["medium.com"],
                "enabled": True
            }
        else:
            return {
                "type": "general",
                "enabled": True
            }