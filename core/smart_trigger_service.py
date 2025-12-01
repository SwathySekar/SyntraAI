# Smart Trigger Service - LLM-based trigger creation using existing infrastructure
from core.llm_workflow_parser import LLMWorkflowParser
from core.trigger_manager import TriggerManager
import datetime

class SmartTriggerService:
    def __init__(self, trigger_manager: TriggerManager):
        self.parser = LLMWorkflowParser()
        self.trigger_manager = trigger_manager
        self.created_triggers = {}
    
    def create_trigger_from_query(self, user_query: str) -> dict:
        """Create intelligent trigger from natural language query"""
        print(f"🧠 Analyzing query: '{user_query}'")
        
        try:
            # Parse workflow intent using LLM
            workflow_intent = self.parser.parse_workflow_intent(user_query)
            
            print(f"📋 Detected: {workflow_intent['trigger_type']} -> {workflow_intent['actions']}")
            print(f"🎯 Confidence: {workflow_intent['confidence']:.2f}")
            
            # Create trigger configuration
            trigger_config = self.parser.create_trigger_config(workflow_intent)
            
            # Register with trigger manager
            trigger = self.trigger_manager.add_trigger(trigger_config)
            
            # Generate unique ID
            trigger_id = f"smart_{datetime.datetime.now().timestamp()}"
            
            # Store trigger info
            self.created_triggers[trigger_id] = {
                "trigger": trigger,
                "workflow_intent": workflow_intent,
                "user_query": user_query,
                "created_at": datetime.datetime.now().isoformat()
            }
            
            return {
                "status": "success",
                "trigger_id": trigger_id,
                "trigger_type": workflow_intent["trigger_type"],
                "actions": workflow_intent["actions"],
                "confidence": workflow_intent["confidence"],
                "output_method": workflow_intent["output_method"]
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to create trigger: {str(e)}"
            }
    
    def get_trigger_recommendations(self, user_query: str) -> dict:
        """Get recommendations for improving the trigger"""
        try:
            workflow_intent = self.parser.parse_workflow_intent(user_query)
            
            recommendations = []
            confidence = workflow_intent.get("confidence", 0)
            
            if confidence < 0.8:
                recommendations.append("Consider being more specific about when the trigger should activate")
            
            actions = workflow_intent.get("actions", [])
            if len(actions) == 0:
                recommendations.append("Specify what action should be performed")
            elif len(actions) > 2:
                recommendations.append("Consider splitting into multiple simpler workflows")
            
            if workflow_intent.get("output_method") == "email" and "email" not in user_query.lower():
                recommendations.append("Email delivery detected but not explicitly requested")
            
            return {
                "status": "success",
                "confidence": confidence,
                "recommendations": recommendations,
                "suggested_improvements": self._get_improvements(workflow_intent)
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Analysis failed: {str(e)}"
            }
    
    def _get_improvements(self, workflow_intent: dict) -> list:
        """Generate specific improvement suggestions"""
        improvements = []
        
        trigger_type = workflow_intent.get("trigger_type")
        if trigger_type == "browser_event":
            improvements.append("Specify which websites or domains to monitor")
        
        conditions = workflow_intent.get("conditions", {})
        if not conditions and trigger_type == "file_download":
            improvements.append("Add file type filters (e.g., 'PDF files only')")
        
        return improvements
    
    def start_trigger(self, trigger_id: str) -> bool:
        """Start a created trigger"""
        if trigger_id in self.created_triggers:
            trigger_info = self.created_triggers[trigger_id]
            trigger_info["trigger"].start()
            print(f"✅ Started trigger: {trigger_id}")
            return True
        return False
    
    def get_active_triggers(self) -> dict:
        """Get information about all created triggers"""
        return {
            "total": len(self.created_triggers),
            "triggers": [
                {
                    "id": tid,
                    "type": info["workflow_intent"]["trigger_type"],
                    "query": info["user_query"],
                    "confidence": info["workflow_intent"]["confidence"],
                    "created": info["created_at"]
                }
                for tid, info in self.created_triggers.items()
            ]
        }