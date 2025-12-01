# Hierarchical Multi-Agent System using Google ADK
from google.adk.agents import Agent
from .tools import process_with_dynamic_query, parse_natural_language, setup_triggers, send_email_delivery

def create_hierarchical_agents():
    """Create hierarchical agent system with proper error handling"""
    try:
        # Define individual specialized agents
        understanding_agent = Agent(
            name="UnderstandingAgent",
            model="gemini-2.0-flash",
            description="Parses natural language workflow requests",
            instruction="Parse user requests into structured workflow format.",
            tools=[parse_natural_language]
        )

        action_agent = Agent(
            name="ActionAgent",
            model="gemini-2.0-flash", 
            description="Processes content dynamically based on user queries",
            instruction="Process content using dynamic LLM queries.",
            tools=[process_with_dynamic_query]
        )

        delivery_agent = Agent(
            name="DeliveryAgent",
            model="gemini-2.0-flash",
            description="Delivers workflow results",
            instruction="Send results via email or popup.",
            tools=[send_email_delivery]
        )

        # Create hierarchical coordinator with sub_agents
        workflow_coordinator = Agent(
            name="WorkflowCoordinator",
            model="gemini-2.0-flash",
            description="Coordinates workflow agents",
            instruction="Delegate tasks to sub-agents: UnderstandingAgent for parsing, ActionAgent for processing, DeliveryAgent for results.",
            sub_agents=[
                understanding_agent,
                action_agent,
                delivery_agent
            ]
        )
        
        return workflow_coordinator, understanding_agent, action_agent, delivery_agent
        
    except Exception as e:
        print(f"Error creating hierarchical agents: {e}")
        return None, None, None, None

# Initialize agents
workflow_coordinator, understanding_agent, action_agent, delivery_agent = create_hierarchical_agents()