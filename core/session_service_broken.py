# ADK-Compatible In-Memory Session Service
from datetime import datetime
from typing import Dict, Optional, List
import uuid
# from google.adk.core import logging, tracing  # Disabled for now

class InMemorySessionService:
    def __init__(self, app_name: str = "workflow_synthesizer"):
        self.app_name = app_name
        self.sessions = {}
        self.results = {}
        self.workflows = []
        self.events = []
        # self.logger = logging.get_logger(f"{app_name}.session_service")
        print(f"Session service initialized: {app_name}")
    
    async def create_session(self, app_name: str, user_id: str, session_id: Optional[str] = None) -> Dict:
        """Create new ADK-compatible session"""
        if session_id is None:
            session_id = str(uuid.uuid4())
        
        # with tracing.start_span("session.create") as span:
        #     span.set_attribute("user_id", user_id)
        #     span.set_attribute("session_id", session_id)
            session = {
                "id": session_id,
                "app_name": app_name,
                "user_id": user_id,
                "created_at": datetime.now().isoformat(),
                "messages": [],
                "status": "active"
            }
            self.sessions[session_id] = session
            
            print(f"Session created: {session_id} for user {user_id}")
            return session
    
    def add_message(self, session_id: str, role: str, content: str):
        """Add message to session"""
        if session_id in self.sessions:
            self.sessions[session_id]["messages"].append({
                "role": role,
                "content": content,
                "timestamp": datetime.now().isoformat()
            })
    
    def store_result(self, session_id: str, result: dict) -> str:
        """Store result with observability"""
        # with tracing.start_span("result.store") as span:
        #     span.set_attribute("session_id", session_id)
        result_id = str(uuid.uuid4())
        stored_result = {
                "id": result_id,
                "session_id": session_id,
                "result": result,
                "created_at": datetime.now().isoformat()
            }
            self.results[result_id] = stored_result
            
            # Maintain size limit
            if len(self.results) > 50:
                oldest_id = min(self.results.keys(), key=lambda k: self.results[k]["created_at"])
                del self.results[oldest_id]
            
            print(f"Result stored: {result_id} type={result.get('type')}")
            return result_id
    
    def get_result(self, result_id: str) -> Optional[dict]:
        """Get result by ID"""
        return self.results.get(result_id)
    
    def get_all_results(self) -> List[Dict]:
        """Get all results"""
        return list(self.results.values())
    
    def store_event(self, event_data: Dict) -> str:
        """Store event with size management"""
        event_id = str(uuid.uuid4())
        event = {
            "id": event_id,
            "timestamp": datetime.now().isoformat(),
            **event_data
        }
        self.events.append(event)
        
        # Maintain size limit
        if len(self.events) > 100:
            self.events.pop(0)
        
        print(f"Event stored: {event_id} type={event_data.get('trigger_type')}")
        return event_id
    
    def get_all_events(self) -> List[Dict]:
        """Get all events"""
        return self.events
    
    def store_workflow(self, workflow_data: Dict) -> Dict:
        """Store workflow"""
        workflow = {
            "id": len(self.workflows) + 1,
            "created_at": datetime.now().isoformat(),
            "status": "active",
            **workflow_data
        }
        self.workflows.append(workflow)
        
        print(f"Workflow stored: {workflow['id']} - {workflow_data.get('query')}")
        return workflow
    
    def get_all_workflows(self) -> List[Dict]:
        """Get all workflows"""
        return self.workflows
    
    def delete_workflow(self, workflow_id: int) -> bool:
        """Delete workflow by ID"""
        for i, workflow in enumerate(self.workflows):
            if workflow["id"] == workflow_id:
                del self.workflows[i]
                print(f"Workflow deleted: {workflow_id}")
                return True
        return False
    
    async def get_session(self, app_name: str, user_id: str, session_id: str) -> Optional[Dict]:
        """Get ADK-compatible session"""
        # with tracing.start_span("session.get") as span:
        #     span.set_attribute("user_id", user_id)
        #     span.set_attribute("session_id", session_id)
            session = self.sessions.get(session_id)
            if session and session.get("user_id") == user_id:
                return session
            return None
