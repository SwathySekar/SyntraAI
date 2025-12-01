# Hierarchical Workflow Processor using ADK Agent Hierarchy
from .hierarchical_orchestrator import workflow_coordinator
from .tools import extract_event_content, process_with_dynamic_query
from typing import Dict, Any
import asyncio

class HierarchicalWorkflowProcessor:
    """Processes workflows using hierarchical ADK agents."""
    
    def __init__(self):
        self.coordinator = workflow_coordinator
        self.active_workflows = []
    
    async def create_workflow(self, user_input: str) -> Dict[str, Any]:
        """Create workflow using hierarchical agent coordination."""
        try:
            if not self.coordinator:
                return {
                    "status": "error",
                    "message": "Hierarchical coordinator not initialized"
                }
            
            # Simple workflow creation without complex ADK calls
            workflow = {
                "user_input": user_input,
                "trigger_type": self._extract_trigger_type(user_input),
                "status": "active",
                "agent_hierarchy": True,
                "config": {"output_preference": "popup"}
            }
            
            self.active_workflows.append(workflow)
            
            return {
                "status": "success",
                "workflow": workflow,
                "message": f"Hierarchical workflow created for: {user_input}"
            }
            
        except Exception as e:
            return {
                "status": "error", 
                "message": f"Failed to create workflow: {str(e)}"
            }
    
    def _extract_trigger_type(self, user_input: str) -> str:
        """Extract trigger type from user input"""
        if "download" in user_input.lower() or "file" in user_input.lower():
            return "file_download"
        elif "email" in user_input.lower() and "compose" in user_input.lower():
            return "email_compose"
        elif "article" in user_input.lower() or "read" in user_input.lower():
            return "article_read"
        return "file_download"
    
    async def process_event(self, event_data: Dict, workflow_config: Dict) -> Dict[str, Any]:
        """Process event using hierarchical agent coordination."""
        try:
            user_query = workflow_config.get('user_input', '')
            content = extract_event_content(event_data)
            
            if not content:
                content = "No content available"
            
            # Use direct tool call instead of complex ADK coordination
            result = process_with_dynamic_query(content, user_query)
            
            output_method = workflow_config.get('config', {}).get('output_preference', 'popup')
            
            return {
                "status": "completed",
                "result": {
                    "type": "result",
                    "content": result.get('result', 'No result'),
                    "success": result.get('success', False)
                },
                "delivery": {
                    "method": output_method,
                    "status": "ready"
                },
                "agent_hierarchy": True
            }
                
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to process event: {str(e)}",
                "agent_hierarchy": True
            }
    
    def get_agent_hierarchy_info(self) -> Dict[str, Any]:
        """Get information about the agent hierarchy."""
        return {
            "coordinator": {
                "name": self.coordinator.name,
                "model": self.coordinator.model,
                "description": self.coordinator.description
            },
            "sub_agents": [
                {
                    "name": agent.name,
                    "model": agent.model, 
                    "description": agent.description,
                    "tools": [tool.__name__ for tool in agent.tools] if agent.tools else []
                }
                for agent in self.coordinator.sub_agents
            ],
            "active_workflows": len(self.active_workflows),
            "hierarchy_enabled": True
        }
    
    async def delegate_to_understanding_agent(self, user_input: str) -> Dict:
        """Directly delegate to understanding agent."""
        prompt = f"Parse workflow request: {user_input}"
        response = await self.coordinator.sub_agents[0].run(prompt)  # UnderstandingAgent
        return {"agent": "UnderstandingAgent", "response": response}
    
    async def delegate_to_action_agent(self, content: str, user_query: str) -> Dict:
        """Directly delegate to action agent."""
        prompt = f"Process content '{content}' based on query '{user_query}'"
        response = await self.coordinator.sub_agents[2].run(prompt)  # ActionAgent
        return {"agent": "ActionAgent", "response": response}
    
    async def delegate_to_delivery_agent(self, results: str, method: str = "email") -> Dict:
        """Directly delegate to delivery agent."""
        prompt = f"Deliver results '{results}' via {method}"
        response = await self.coordinator.sub_agents[3].run(prompt)  # DeliveryAgent
        return {"agent": "DeliveryAgent", "response": response}