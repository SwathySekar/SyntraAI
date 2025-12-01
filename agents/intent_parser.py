# Intent Parser Agent
from config import GEMINI_API_KEY

class IntentParserAgent:
    def __init__(self):
        self.api_key = GEMINI_API_KEY
    
    def parse_intent(self, event_data: dict) -> dict:
        """Parse user intent from event data"""
        event_type = event_data.get('event_type', 'unknown')
        
        if event_type == 'article_read':
            return {
                "intent": "summarize_article",
                "action": "generate_summary",
                "output_type": "summary",
                "confidence": 0.95
            }
        
        elif event_type == 'email_compose':
            return {
                "intent": "analyze_email",
                "action": "provide_feedback",
                "output_type": "feedback",
                "confidence": 0.90
            }
        
        elif event_type == 'file_download' and event_data.get('file_name', '').endswith('.pdf'):
            return {
                "intent": "extract_data",
                "action": "parse_and_categorize",
                "output_type": "report",
                "confidence": 0.85
            }
        
        return {
            "intent": "unknown",
            "action": "log_only",
            "output_type": "none",
            "confidence": 0.0
        }
