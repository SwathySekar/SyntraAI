# LLM-Based Natural Language Workflow Parser
import re
import json
from google import genai
from config import GEMINI_API_KEY

class WorkflowParser:
    def __init__(self):
        self.client = genai.Client(api_key=GEMINI_API_KEY)
        self.model = "gemini-2.0-flash-exp"
    
    def parse(self, natural_language: str) -> dict:
        """Parse natural language using LLM for intelligent trigger creation"""
        try:
            # Use LLM to analyze user query and create trigger
            workflow_config = self._llm_parse_workflow(natural_language)
            return workflow_config
        except Exception as e:
            # Fallback to basic parsing if LLM fails
            print(f"LLM parsing failed: {e}, using fallback")
            return self._fallback_parse(natural_language)
    
    def _llm_parse_workflow(self, user_query: str) -> dict:
        """Use LLM to intelligently parse workflow and create triggers"""
        prompt = f"""Analyze this workflow request and create a trigger configuration:

User Query: "{user_query}"

You need to identify:
1. TRIGGER TYPE: What event should start this workflow?
   - file_download: When files are downloaded/added to folders
   - email_compose: When composing/writing emails
   - article_read: When reading articles/blogs
   - browser_event: When visiting specific websites
   - time_based: Scheduled/recurring events

2. CONDITIONS: What specific conditions must be met?
   - file_extension: .pdf, .doc, etc.
   - domains: medium.com, gmail.com, etc.
   - folder_path: specific directories to monitor
   - file_size: minimum/maximum file sizes
   - keywords: specific text to look for

3. ACTIONS: What should happen when triggered?
   - summarize: Create summary/key points
   - analyze_tone: Analyze writing tone/sentiment
   - extract_text: Extract and parse content
   - notify_file: Send notifications about files
   - elaborate: Provide detailed analysis
   - suggest: Give recommendations/improvements

4. OUTPUT CONFIG: How should results be delivered?
   - output_preference: "email", "popup", "save_file"
   - recipient_email: email address if applicable
   - detail_level: 1-5 scale for depth

Return ONLY valid JSON in this exact format:
{{
  "trigger_type": "...",
  "conditions": {{
    "file_extension": "...",
    "domains": [...],
    "folder_path": "...",
    "keywords": [...]
  }},
  "actions": [...],
  "config": {{
    "points": 3,
    "output_preference": "...",
    "recipient_email": "...",
    "detail_level": 3
  }}
}}"""

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt
        )
        
        # Clean and parse JSON response
        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:-3]
        elif text.startswith("```"):
            text = text[3:-3]
        
        return json.loads(text.strip())
    
    def _fallback_parse(self, natural_language: str) -> dict:
        """Fallback parsing when LLM is unavailable"""
        nl = natural_language.lower()
        
        # Basic trigger detection
        if any(word in nl for word in ['download', 'file', 'pdf']):
            trigger_type = "file_download"
        elif any(word in nl for word in ['email', 'compose', 'write']):
            trigger_type = "email_compose"
        elif any(word in nl for word in ['article', 'medium', 'read']):
            trigger_type = "article_read"
        else:
            trigger_type = "general"
        
        # Basic action detection
        actions = []
        if any(word in nl for word in ['summarize', 'summary']):
            actions.append('summarize')
        if any(word in nl for word in ['analyze', 'tone']):
            actions.append('analyze_tone')
        if any(word in nl for word in ['notify', 'alert']):
            actions.append('notify_file')
        
        if not actions:
            actions = ['summarize'] if trigger_type == "article_read" else ['notify_file']
        
        # Basic conditions
        conditions = {}
        if "pdf" in nl:
            conditions["file_extension"] = ".pdf"
        
        return {
            "trigger_type": trigger_type,
            "conditions": conditions,
            "actions": actions,
            "config": {
                "points": 3,
                "output_preference": "popup",
                "recipient_email": None
            }
        }
    
    def create_trigger_from_workflow(self, workflow_config: dict) -> dict:
        """Create actual trigger configuration from parsed workflow"""
        trigger_type = workflow_config.get("trigger_type")
        conditions = workflow_config.get("conditions", {})
        
        # Generate trigger configuration based on type
        if trigger_type == "file_download":
            return {
                "type": "file_watcher",
                "folder_path": conditions.get("folder_path", "~/Downloads"),
                "events": ["create", "modify"],
                "file_filter": f"*{conditions.get('file_extension', '.*')}",
                "enabled": True
            }
        elif trigger_type == "email_compose":
            return {
                "type": "browser_event",
                "event": "email_compose",
                "domains": conditions.get("domains", ["mail.google.com"]),
                "enabled": True
            }
        elif trigger_type == "article_read":
            return {
                "type": "browser_event",
                "event": "article_read",
                "domains": conditions.get("domains", ["medium.com"]),
                "enabled": True
            }
        else:
            return {
                "type": "general",
                "enabled": True,
                "conditions": conditions
            }

    def analyze_trigger_intent(self, user_query: str) -> dict:
        """Analyze user intent for trigger creation using LLM"""
        prompt = f"""Analyze this user request for workflow automation:

Query: "{user_query}"

Determine:
1. What EVENT should trigger this workflow? (be specific)
2. What CONDITIONS must be met?
3. What ACTIONS should be performed?
4. How should RESULTS be delivered?

Provide analysis in JSON format:
{{
  "trigger_event": "specific event description",
  "trigger_confidence": 0.95,
  "suggested_conditions": ["condition1", "condition2"],
  "recommended_actions": ["action1", "action2"],
  "delivery_method": "email/popup/file",
  "complexity_score": 3
}}"""

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt
            )
            
            text = response.text.strip()
            if text.startswith("```json"):
                text = text[7:-3]
            elif text.startswith("```"):
                text = text[3:-3]
            
            return json.loads(text.strip())
        except Exception as e:
            return {
                "trigger_event": "general_event",
                "trigger_confidence": 0.5,
                "suggested_conditions": [],
                "recommended_actions": ["notify"],
                "delivery_method": "popup",
                "complexity_score": 1
            }