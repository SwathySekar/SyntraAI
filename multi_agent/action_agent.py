# Action Agent - Executes dynamic actions based on user queries
from google.adk.agents import Agent



def process_with_dynamic_query(content: str, user_query: str) -> dict:
    """Process content dynamically based on user query using LLM."""
    from tools.summarizer import LLMProcessor
    
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

class ActionAgent:
    def __init__(self):
        
        # Google ADK Agent
        self.adk_agent = Agent(
            name="action_adk",
            model="gemini-2.0-flash",
            description="Executes dynamic workflow actions on content based on user queries",
            instruction="You process content dynamically based on user queries. Use process_with_dynamic_query for all content processing.",
            tools=[process_with_dynamic_query]
        )
    
    async def execute_action(self, user_query: str, event_data: dict, config: dict) -> dict:
        """Execute dynamic action based on user query"""
        return await self._process_dynamically(user_query, event_data, config)
    

    
    async def _process_dynamically(self, user_query: str, event_data: dict, config: dict) -> dict:
        """Process content dynamically based on user query"""
        content = self._extract_content(event_data)
        
        if not content:
            return {
                "action": "dynamic_processing",
                "result": "No content available to process",
                "success": False,
                "user_query": user_query
            }
        
        # Use dynamic processing tool
        return process_with_dynamic_query(content, user_query)
    
    def _extract_content(self, event_data: dict) -> str:
        """Extract content from different event types"""
        # File events - Read actual file content
        if 'file_path' in event_data:
            file_path = event_data['file_path']
            file_name = event_data.get('file_name', 'Unknown')
            
            # Handle PDF files
            if file_name.lower().endswith('.pdf'):
                try:
                    from tools.pdf_parser import PDFParserTool
                    pdf_parser = PDFParserTool()
                    result = pdf_parser.extract_text(file_path)
                    if result.get('success'):
                        return f"File: {file_name}\n\nContent:\n{result.get('text', '')[:5000]}"
                    else:
                        return f"File: {file_name}\nNote: Could not extract PDF content"
                except Exception as e:
                    return f"File: {file_name}\nNote: PDF parsing error - {str(e)}"
            
            # Handle text files
            else:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()[:10000]  # First 10KB
                    return f"File: {file_name}\n\nContent:\n{content}"
                except Exception as e:
                    return f"File: {file_name}\nNote: Could not read file - {str(e)}"
        
        # File events without path - just filename
        elif 'file_name' in event_data:
            return f"File downloaded: {event_data.get('file_name', 'Unknown file')}"
        
        # Email events
        elif 'email_subject' in event_data or 'email_body' in event_data:
            subject = event_data.get('email_subject', '')
            body = event_data.get('email_body', '')
            return f"Subject: {subject}\nBody: {body}" if body else f"Subject: {subject}"
        
        # Article events  
        elif 'title' in event_data and 'content' in event_data:
            title = event_data.get('title', '')
            content = event_data.get('content', '')
            return f"Title: {title}\nContent: {content}"
        
        return event_data.get('content', '')
