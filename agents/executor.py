# Executor Agent
from tools.summarizer import LLMProcessor
from tools.pdf_parser import PDFParserTool
from datetime import datetime
import uuid

class ExecutorAgent:
    def __init__(self):
        self.llm_processor = LLMProcessor()
        self.pdf_parser = PDFParserTool()
        self.results = {}
    
    def execute(self, intent: dict, event_data: dict) -> dict:
        """Execute workflow based on user query using LLM"""
        result_id = str(uuid.uuid4())
        
        # Get user query from workflow config
        workflow_config = event_data.get('workflow_config', {})
        user_query = workflow_config.get('query', '')
        
        result = self._process_with_llm(user_query, event_data)
        
        # Store result
        result['id'] = result_id
        result['created_at'] = datetime.now().isoformat()
        result['event_data'] = event_data
        self.results[result_id] = result
        
        return result
    
    def _process_with_llm(self, user_query: str, event_data: dict) -> dict:
        """Process any event using LLM based on user query"""
        print(f"📝 User Query: {user_query}")
        
        # Extract content based on event type
        content = self._extract_content(event_data)
        print(f"📜 Extracted Content: {content[:200]}...")
        
        if not content:
            return {
                "type": "result",
                "content": "No content available to process",
                "success": False
            }
        
        # Use LLM to process content based on user query
        result = self.llm_processor.process_with_query(content, user_query)
        
        print(f"🤖 LLM Result: {result.get('response', 'No response')[:100]}...")
        
        return {
            "type": "result",
            "content": result.get('response', 'No content available'),
            "title": "Workflow Result",
            "success": result.get('success', False)
        }
    
    def _extract_content(self, event_data: dict) -> str:
        """Extract content from different event types"""
        # File events
        if 'file_path' in event_data:
            file_path = event_data['file_path']
            file_name = event_data.get('file_name', '')
            
            if file_name.lower().endswith('.pdf'):
                pdf_result = self.pdf_parser.extract_text(file_path)
                return pdf_result.get('text', '') if pdf_result.get('success') else ''
            else:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        return f.read()[:10000]  # First 10KB
                except:
                    return f"File: {file_name}"
        
        # Email events
        elif 'email_subject' in event_data:
            subject = event_data.get('email_subject', '')
            body = event_data.get('email_body', '')
            to_email = event_data.get('email_to', '')
            return f"Subject: {subject}\nTo: {to_email}\nBody: {body}" if body else f"Email Subject: {subject}\nTo: {to_email}\nNote: Email body not captured."
        
        # Article events  
        elif 'title' in event_data and event_data.get('event_type') == 'article_read':
            title = event_data.get('title', '')
            content = event_data.get('content', '')
            url = event_data.get('url', '')
            return f"Title: {title}\nURL: {url}\nContent: {content}" if content else f"Article: {title}\nURL: {url}"
        
        return ''
    
    def get_result(self, result_id: str) -> dict:
        """Get stored result"""
        return self.results.get(result_id)
