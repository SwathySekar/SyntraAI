# Orchestrator Agent - Coordinates all agents using Google ADK pattern with LLM triggers
from typing import Dict, List
from google.adk.agents import Agent
import datetime
from zoneinfo import ZoneInfo

def coordinate_workflow(user_input: str, event_data: dict = None) -> dict:
    """Coordinate complete workflow execution."""
    if event_data is None:
        # Setup phase
        return {"status": "setup", "message": f"Workflow setup for: {user_input}"}
    else:
        # Execution phase
        return {"status": "executed", "message": "Workflow completed successfully"}

def get_workflow_status() -> dict:
    """Get status of all active workflows."""
    return {"active_workflows": 3, "completed_today": 12}

class OrchestratorAgent:
    def __init__(self, understanding_agent, trigger_agent, action_agent, delivery_agent, llm_trigger_agent=None):
        self.understanding = understanding_agent
        self.trigger = trigger_agent
        self.action = action_agent
        self.delivery = delivery_agent
        self.llm_trigger = llm_trigger_agent  # New LLM-based trigger agent
        self.active_workflows = []
        
        # Google ADK Agent for orchestration
        self.adk_agent = Agent(
            name="orchestrator_adk",
            model="gemini-2.0-flash",
            description="Coordinates all workflow agents using Google ADK",
            instruction="You coordinate workflow execution across understanding, trigger, action, and delivery agents.",
            tools=[coordinate_workflow, get_workflow_status]
        )
    
    async def process_user_request(self, user_input: str) -> Dict:
        """Main orchestration: User input → LLM-based workflow setup"""
        print(f"🎯 Orchestrator: Processing '{user_input}' with LLM intelligence")
        
        # Use LLM-based trigger agent if available
        if self.llm_trigger:
            print("🧠 Using LLM-based trigger creation")
            
            # Create intelligent trigger from user query
            trigger_result = await self.llm_trigger.create_trigger_from_query(user_input)
            
            if trigger_result["status"] == "success":
                workflow = {
                    "trigger": trigger_result["trigger_type"],
                    "actions": trigger_result["actions"],
                    "output": "email",  # Default, can be enhanced
                    "trigger_id": trigger_result["trigger_id"],
                    "user_input": user_input,
                    "confidence": trigger_result["confidence"],
                    "llm_created": True
                }
                
                self.active_workflows.append(workflow)
                print(f"✅ LLM Workflow created with {workflow['confidence']:.2f} confidence")
                return {"status": "active", "workflow": workflow}
            else:
                print(f"⚠️ LLM trigger creation failed: {trigger_result['message']}")
                # Fall back to traditional method
        
        # Fallback: Traditional workflow creation
        print("🔄 Using traditional workflow creation")
        workflow = await self.understanding.parse_workflow(user_input)
        print(f"📋 Understood: {workflow['trigger']} → {workflow['actions']} → {workflow['output']}")
        
        # Set up traditional trigger
        trigger_id = await self.trigger.setup_trigger(workflow['trigger'], workflow.get('conditions', {}))
        workflow['trigger_id'] = trigger_id
        workflow['user_input'] = user_input
        workflow['llm_created'] = False
        self.active_workflows.append(workflow)
        
        return {"status": "active", "workflow": workflow}
    
    async def handle_event(self, event_data: Dict, workflow_config: Dict = None) -> Dict:
        """Event triggered → Execute workflow dynamically"""
        print(f"⚡ Orchestrator: Event {event_data.get('event_type')}")
        
        # Use provided workflow or find matching one
        if workflow_config:
            workflow = workflow_config
            user_query = workflow.get('query', '')
            print(f"✅ Using provided workflow: {user_query}")
        else:
            # Find matching workflow from active workflows
            matching = [w for w in self.active_workflows if self._matches(w, event_data)]
            if not matching:
                return {"status": "no_match"}
            
            workflow = matching[0]
            user_query = workflow.get('user_input', '')
            print(f"✅ Matched workflow: {user_query}")
        
        # Dynamic Action Processing - Use user query instead of predefined actions
        result = await self.action.execute_action(user_query, event_data, workflow.get('config', {}))
        results = [result]
        print(f"🔧 Dynamic processing completed for query: '{user_query}'")
        
        # Determine delivery method
        output_method = workflow.get('config', {}).get('output_preference', 'popup')
        
        # Agent 4: Delivery - Send results
        delivery_result = await self.delivery.deliver(results, output_method, event_data)
        print(f"📤 Delivered via {output_method}: {delivery_result['status']}")
        
        return {"status": "completed", "results": results, "delivery": delivery_result}
    
    def _matches(self, workflow: Dict, event: Dict) -> bool:
        """Check if event matches workflow trigger"""
        workflow_trigger = workflow.get('trigger') or workflow.get('trigger_type')
        return workflow_trigger == event.get('event_type')
    
    def get_active_workflows(self) -> List[Dict]:
        """Get all active workflows with LLM status"""
        return self.active_workflows
    
    def get_llm_trigger_stats(self) -> Dict:
        """Get statistics about LLM vs traditional triggers"""
        if not self.llm_trigger:
            return {"llm_available": False}
        
        llm_workflows = [w for w in self.active_workflows if w.get('llm_created', False)]
        traditional_workflows = [w for w in self.active_workflows if not w.get('llm_created', False)]
        
        return {
            "llm_available": True,
            "total_workflows": len(self.active_workflows),
            "llm_created": len(llm_workflows),
            "traditional_created": len(traditional_workflows),
            "llm_percentage": len(llm_workflows) / len(self.active_workflows) * 100 if self.active_workflows else 0,
            "average_confidence": sum(w.get('confidence', 0) for w in llm_workflows) / len(llm_workflows) if llm_workflows else 0
        }
