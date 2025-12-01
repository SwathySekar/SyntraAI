#!/usr/bin/env python3
"""Unified server for both file and browser triggers"""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from core.trigger_manager import TriggerManager
from agents.intent_parser import IntentParserAgent
from agents.executor import ExecutorAgent
from multi_agent.orchestrator import OrchestratorAgent
from multi_agent.understanding_agent import UnderstandingAgent
from multi_agent.trigger_agent import TriggerAgent
from multi_agent.action_agent import ActionAgent
from multi_agent.delivery_agent import DeliveryAgent
from multi_agent.hierarchical_processor import HierarchicalWorkflowProcessor
from core.workflow_parser import WorkflowParser
from core.session_service import InMemorySessionService
from core.smart_trigger_service import SmartTriggerService
from typing import Dict, List
from datetime import datetime
import os
import asyncio

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

APP_NAME = "syntra"
DEFAULT_USER_ID = "user_001"
user_preferences: Dict = {"default_method": "ask", "email": ""}
trigger_manager = TriggerManager()
intent_parser = IntentParserAgent()
executor = ExecutorAgent()  # Keep for backward compatibility
workflow_parser = WorkflowParser()
session_service = InMemorySessionService(APP_NAME)
smart_trigger_service = SmartTriggerService(trigger_manager)

# Initialize Multi-Agent System
understanding_agent = UnderstandingAgent()
trigger_agent = TriggerAgent(trigger_manager)
action_agent = ActionAgent()
delivery_agent = DeliveryAgent()
orchestrator = OrchestratorAgent(
    understanding_agent=understanding_agent,
    trigger_agent=trigger_agent,
    action_agent=action_agent,
    delivery_agent=delivery_agent
)

# Initialize Hierarchical ADK Agent System
hierarchical_processor = HierarchicalWorkflowProcessor()

print(f"Server starting: {APP_NAME}")

# Track processed events to avoid duplicates
processed_events = set()

def handle_trigger_event(event):
    """Callback for all trigger events with better event formatting"""
    # Create unique event ID to prevent duplicate processing
    event_id = f"{event.payload.get('event_type', 'unknown')}_{event.payload.get('email_subject', '')}_{event.payload.get('timestamp', '')}"
    
    if event_id in processed_events:
        print(f"⏭️ Skipping duplicate event: {event_id}")
        return
    
    processed_events.add(event_id)
    print(f"🔔 CALLBACK TRIGGERED: {event}")
    print(f"📦 Event payload: {event.payload}")
    
    # Determine event type and format payload
    if 'file_name' in event.payload:
        event_type = 'file_download'
        title = event.payload['file_name']
        description = f"Downloaded: {event.payload['file_name']}"
    elif 'email_subject' in event.payload:
        event_type = 'email_compose'
        title = event.payload['email_subject']
        description = f"Email: {event.payload['email_subject']}"
    elif event.payload.get('event_type') == 'article_read' or ('title' in event.payload and 'content' in event.payload):
        event_type = 'article_read'
        title = event.payload.get('title', 'Article')
        description = f"Article: {title}"
    else:
        event_type = 'unknown'
        title = 'Unknown Event'
        description = 'Unknown event type'
    
    print(f"🎯 Detected event type: {event_type} - {title}")
    
    # Ensure file details are properly passed
    enhanced_payload = {
        **event.payload,
        "event_type": event_type,
        "title": title,
        "description": description
    }
    
    event_data = {
        "trigger_type": event.trigger_type,
        "timestamp": event.timestamp.isoformat(),
        "payload": enhanced_payload
    }
    
    session_service.store_event(event_data)
    print(f"💾 Event stored: {event_type} - {title}")
    
    # Process event based on type
    if event_type == 'file_download':
        print(f"📁 Processing as file download")
        process_file_event_sync(enhanced_payload)
    elif event_type in ['email_compose', 'article_read']:
        print(f"🌐 Processing as browser event")
        asyncio.create_task(process_event_with_agents(enhanced_payload))
    else:
        print(f"❓ Unknown event type: {event_type}")

def setup_triggers():
    """Setup triggers only when workflows exist"""
    # Don't start any triggers by default
    # Triggers will be started when workflows are added
    pass

# Global trigger tracking
active_triggers = {}

def start_trigger_for_workflow(workflow):
    """Start specific trigger based on workflow (avoid duplicates)"""
    trigger_type = workflow.get('trigger_type')
    
    # Check if trigger already exists for this type
    if trigger_type in active_triggers:
        print(f"♾️ Trigger already active for {trigger_type}")
        return
    
    if trigger_type == 'file_download':
        file_config = {
            "type": "file_watcher",
            "folder_path": os.path.expanduser("~/Downloads"),
            "events": ["create"],
            "file_filter": "*",
            "enabled": True,
            "workflow_id": workflow['id']
        }
        print(f"🔧 Creating file trigger for: {os.path.expanduser('~/Downloads')}")
        file_trigger = trigger_manager.add_trigger(file_config)
        
        if file_trigger:
            file_trigger.register_callback(handle_trigger_event)
            file_trigger.start()
            print(f"✅ File trigger started and watching Downloads folder")
        else:
            print(f"❌ Failed to create file trigger")
        
        active_triggers[trigger_type] = file_trigger
        print(f"📁 Started file trigger for workflow: {workflow['query']}")
    
    elif trigger_type == 'email_compose':
        browser_config = {
            "type": "browser_event",
            "event": "email_compose",
            "domains": ["mail.google.com"],
            "enabled": True,
            "workflow_id": workflow['id']
        }
        browser_trigger = trigger_manager.add_trigger(browser_config)
        browser_trigger.register_callback(handle_trigger_event)
        browser_trigger.start()
        active_triggers[trigger_type] = browser_trigger
        print(f"📧 Started email trigger for workflow: {workflow['query']}")
    
    elif trigger_type == 'article_read':
        medium_config = {
            "type": "browser_event",
            "event": "article_read",
            "domains": ["medium.com"],
            "enabled": True,
            "workflow_id": workflow['id']
        }
        medium_trigger = trigger_manager.add_trigger(medium_config)
        medium_trigger.register_callback(handle_trigger_event)
        medium_trigger.start()
        active_triggers[trigger_type] = medium_trigger
        print(f"📖 Started medium trigger for workflow: {workflow['query']}")

@app.on_event("startup")
async def startup():
    setup_triggers()

@app.post("/event")
async def receive_event(event_data: Dict):
    """Receive browser events"""
    handle_trigger_event(type('Event', (), {
        'trigger_type': 'BrowserTrigger',
        'timestamp': __import__('datetime').datetime.now(),
        'payload': event_data
    })())
    
    asyncio.create_task(process_event_with_agents(event_data))
    return {"status": "received"}

def process_file_event_sync(event_data: Dict):
    """Process file event synchronously"""
    try:
        file_name = event_data.get('file_name', 'Unknown file')
        file_path = event_data.get('file_path', 'Downloads')
        file_size = event_data.get('size', 0)
        
        print(f"📁 Processing file event: {file_name} ({file_size} bytes)")
        
        all_workflows = session_service.get_all_workflows()
        matching_workflows = [w for w in all_workflows if w['status'] == 'active' and w['trigger_type'] == 'file_download']
        
        print(f"🔍 Found {len(matching_workflows)} matching workflows")
        
        if matching_workflows:
            workflow = matching_workflows[0]
            print(f"✅ Using workflow: {workflow['query']}")
            print(f"🔍 Workflow trigger_type: {workflow.get('trigger_type')}")
            print(f"🔍 Event trigger matching: file_download")
            
            # Use LLM processing for all file events
            intent = {'action': 'process_with_llm', 'intent': 'file_event'}
            
            # Ensure all file details and query are passed to executor
            enhanced_event_data = {
                **event_data,
                'file_name': file_name,
                'file_path': file_path,
                'file_size': file_size,
                'workflow_config': {**workflow.get('config', {}), 'query': workflow['query']}
            }
            
            print(f"📝 File workflow query being passed: {workflow['query']}")
            
            print(f"🎯 Processing file with Multi-Agent System: {file_name}")
            
            # Use orchestrator for multi-agent processing
            orchestrator_result = asyncio.run(orchestrator.handle_event(
                enhanced_event_data, 
                workflow_config=workflow
            ))
            
            # Extract result for compatibility
            if orchestrator_result.get('status') == 'completed':
                raw_result = orchestrator_result['results'][0] if orchestrator_result['results'] else {}
                print(f"🔍 Raw result from orchestrator: {raw_result}")
                
                # Extract content from nested result structure
                content = raw_result.get('result', raw_result.get('content', 'No content generated'))
                print(f"📝 Extracted content length: {len(str(content))} chars")
                
                # Ensure proper result format with all required fields
                result = {
                    'type': 'result',
                    'content': content,
                    'title': file_name,
                    'success': raw_result.get('success', True),
                    'created_at': datetime.now().isoformat(),
                    'event_type': 'file_download',
                    'file_size': file_size
                }
            else:
                # Fallback to original executor
                print(f"🔄 Falling back to original executor")
                result = executor.execute(intent, enhanced_event_data)
            
            session_service.store_result("default_session", result)
            
            print(f"📊 File result: {result.get('type')} - Content length: {len(str(result.get('content', '')))} chars")
            
            # Email already sent by orchestrator's delivery agent, no need to send again
            workflow_config = enhanced_event_data.get('workflow_config', {})
            if workflow_config.get('output_preference') == 'email':
                print(f"📧 Email already sent by delivery agent")
            else:
                print(f"💬 Result ready for popup display")
        else:
            print(f"⚠️ No matching workflows found for file event")
            print(f"🔍 Available workflows: {[(w['id'], w['trigger_type'], w['query']) for w in all_workflows]}")
            print(f"🔍 Looking for trigger_type: file_download")
    except Exception as e:
        print(f"❌ File processing error: {e}")
        import traceback
        traceback.print_exc()

async def process_event_with_agents(event_data: Dict):
    """Process event through agent pipeline"""
    try:
        event_type = event_data.get('event_type', 'unknown')
        print(f"🌐 Processing browser event: {event_type}")
        
        all_workflows = session_service.get_all_workflows()
        # Match workflow by trigger type
        matching_workflows = [w for w in all_workflows if w['status'] == 'active' and w['trigger_type'] == event_type]
        
        if matching_workflows:
            workflow = matching_workflows[0]
            print(f"✅ Using workflow: {workflow['query']}")
            
            # Pass user query to executor
            enhanced_event_data = {
                **event_data,
                'workflow_config': {**workflow.get('config', {}), 'query': workflow['query']}
            }
            
            print(f"🎯 Processing browser event with Multi-Agent System: {event_type}")
            
            # Use orchestrator for multi-agent processing
            orchestrator_result = await orchestrator.handle_event(
                enhanced_event_data,
                workflow_config=workflow
            )
            
            # Extract result for compatibility
            if orchestrator_result.get('status') == 'completed':
                raw_result = orchestrator_result['results'][0] if orchestrator_result['results'] else {}
                print(f"🔍 Raw result from orchestrator: {raw_result}")
                
                # Extract content from nested result structure
                content = raw_result.get('result', raw_result.get('content', 'No content generated'))
                print(f"📝 Extracted content length: {len(str(content))} chars")
                
                # Ensure proper result format with all required fields
                result = {
                    'type': 'result',
                    'content': content,
                    'title': event_data.get('email_subject', event_data.get('title', 'Workflow Result')),
                    'success': raw_result.get('success', True),
                    'created_at': datetime.now().isoformat(),
                    'event_type': event_type
                }
            else:
                # Fallback to original executor
                print(f"🔄 Falling back to original executor")
                intent = {'action': 'process_with_llm', 'intent': 'browser_event'}
                result = executor.execute(intent, enhanced_event_data)
            
            session_service.store_result("default_session", result)
            
            print(f"📊 Browser result: {result.get('type')} - Content length: {len(str(result.get('content', '')))} chars")
        else:
            print(f"⚠️ No matching workflows found for {event_type} event")
    except Exception as e:
        print(f"❌ Agent error: {e}")
        import traceback
        traceback.print_exc()

@app.get("/events")
async def get_events():
    """Get all events"""
    events = session_service.get_all_events()
    return {"events": events}

@app.get("/results")
async def get_results():
    """Get all results"""
    results = session_service.get_all_results()
    return {"results": [r["result"] for r in results]}

@app.get("/workflows")
async def get_workflows():
    """Get all workflows"""
    workflows = session_service.get_all_workflows()
    return {"workflows": workflows}

@app.post("/workflow")
async def add_workflow(workflow_data: Dict):
    """Add workflow with smart trigger creation and multi-agent support"""
    query = workflow_data.get("query", "")
    use_smart = workflow_data.get("use_smart", True)
    use_multi_agent = workflow_data.get("use_multi_agent", True)
    use_hierarchy = workflow_data.get("use_hierarchy", False)
    
    if use_smart:
        print(f"🧠 Creating smart trigger for: '{query}'")
        # Use smart trigger service
        smart_result = smart_trigger_service.create_trigger_from_query(query)
        
        if smart_result["status"] == "success":
            workflow_config = {
                "query": query,
                "trigger_type": smart_result["trigger_type"],
                "conditions": {},
                "actions": smart_result["actions"],
                "config": {
                    "output_preference": smart_result["output_method"],
                    "confidence": smart_result["confidence"],
                    "smart_created": True
                }
            }
            
            workflow = session_service.store_workflow(workflow_config)
            
            # Add to appropriate system
            if use_hierarchy:
                hierarchy_result = await hierarchical_processor.create_workflow(query)
                print(f"🏗️ Added workflow to hierarchical ADK system")
            elif use_multi_agent:
                orchestrator.active_workflows.append({
                    "trigger_type": workflow['trigger_type'],
                    "user_input": query,
                    "config": workflow['config'],
                    "workflow_id": workflow['id']
                })
                print(f"🤖 Added workflow to multi-agent orchestrator")
            
            # Start trigger using existing method
            start_trigger_for_workflow(workflow)
            
            print(f"✅ Smart workflow created and trigger started")
            return {
                "status": "created", 
                "workflow": workflow,
                "multi_agent_enabled": use_multi_agent,
                "hierarchy_enabled": use_hierarchy
            }
        else:
            print(f"⚠️ Smart trigger failed: {smart_result['message']}, using traditional")
    
    # Fallback to traditional workflow creation
    print(f"🔄 Using traditional workflow parsing")
    parsed = workflow_parser.parse(query)
    
    workflow_config = {
        "query": query,
        "trigger_type": parsed["trigger_type"],
        "conditions": parsed["conditions"],
        "actions": parsed["actions"],
        "config": {**parsed["config"], "smart_created": False}
    }
    
    workflow = session_service.store_workflow(workflow_config)
    
    # Add to appropriate system
    if use_hierarchy:
        hierarchy_result = await hierarchical_processor.create_workflow(query)
        print(f"🏗️ Added workflow to hierarchical ADK system")
    elif use_multi_agent:
        orchestrator.active_workflows.append({
            "trigger_type": workflow['trigger_type'],
            "user_input": query,
            "config": workflow['config'],
            "workflow_id": workflow['id']
        })
        print(f"🤖 Added workflow to multi-agent orchestrator")
    
    # Start trigger for this workflow
    try:
        start_trigger_for_workflow(workflow)
        print(f"✅ Traditional workflow ready: {workflow['query']}")
    except Exception as e:
        print(f"❌ Failed to start trigger: {e}")
    
    return {"status": "created", "workflow": workflow, "multi_agent_enabled": use_multi_agent, "hierarchy_enabled": use_hierarchy}

@app.delete("/workflow/{workflow_id}")
async def delete_workflow(workflow_id: int):
    """Delete workflow"""
    success = session_service.delete_workflow(workflow_id)
    return {"status": "deleted" if success else "not_found"}

@app.get("/dashboard")
async def dashboard():
    """Serve dashboard"""
    with open("unified_dashboard.html", "r") as f:
        return HTMLResponse(content=f.read())

@app.get("/stats")
async def get_stats():
    """Get statistics"""
    events = session_service.get_all_events()
    workflows = session_service.get_all_workflows()
    results = session_service.get_all_results()
    
    smart_triggers = smart_trigger_service.get_active_triggers()
    smart_workflows = [w for w in workflows if w.get('config', {}).get('smart_created', False)]
    
    return {
        "total_events": len(events),
        "email_events": sum(1 for e in events if e.get('payload', {}).get('event_type') == 'email_compose'),
        "file_events": sum(1 for e in events if 'file_name' in e.get('payload', {})),
        "article_events": 0,
        "active_workflows": len([w for w in workflows if w['status'] == 'active']),
        "results_generated": len(results),
        "smart_triggers": smart_triggers["total"],
        "smart_workflows": len(smart_workflows),
        "avg_confidence": sum(w.get('config', {}).get('confidence', 0) for w in smart_workflows) / len(smart_workflows) if smart_workflows else 0
    }

@app.post("/send-email")
async def send_email_endpoint(email_data: Dict):
    """Send email"""
    try:
        from multi_agent.delivery_agent import DeliveryAgent
        delivery = DeliveryAgent()
        
        result = email_data.get('result', {})
        recipient = email_data.get('recipient', 'swathyecengg@gmail.com')
        
        results = [result]
        event_data = {'user_email': recipient}
        
        delivery_result = await delivery._send_email(results, event_data)
        return delivery_result
    except Exception as e:
        return {"status": "failed", "error": str(e)}

@app.post("/smart-trigger")
async def create_smart_trigger(trigger_data: Dict):
    """Create smart trigger from natural language"""
    query = trigger_data.get("query", "")
    
    if not query:
        return {"status": "error", "message": "Query is required"}
    
    result = smart_trigger_service.create_trigger_from_query(query)
    
    if result["status"] == "success":
        # Start the trigger
        smart_trigger_service.start_trigger(result["trigger_id"])
    
    return result

@app.get("/smart-triggers")
async def get_smart_triggers():
    """Get all smart triggers"""
    return smart_trigger_service.get_active_triggers()

@app.post("/analyze-query")
async def analyze_query(query_data: Dict):
    """Analyze query and get recommendations"""
    query = query_data.get("query", "")
    
    if not query:
        return {"status": "error", "message": "Query is required"}
    
    return smart_trigger_service.get_trigger_recommendations(query)

@app.get("/multi-agent-stats")
async def get_multi_agent_stats():
    """Get multi-agent system statistics"""
    return {
        "orchestrator_active": True,
        "active_workflows": len(orchestrator.active_workflows),
        "agents_initialized": {
            "understanding_agent": understanding_agent is not None,
            "trigger_agent": trigger_agent is not None,
            "action_agent": action_agent is not None,
            "delivery_agent": delivery_agent is not None
        },
        "workflows": [{
            "trigger_type": w.get('trigger_type'),
            "user_input": w.get('user_input', '')[:50] + '...' if len(w.get('user_input', '')) > 50 else w.get('user_input', ''),
            "workflow_id": w.get('workflow_id')
        } for w in orchestrator.active_workflows]
    }

@app.get("/hierarchy-stats")
async def get_hierarchy_stats():
    """Get hierarchical ADK agent system statistics"""
    return hierarchical_processor.get_agent_hierarchy_info()

@app.post("/test-hierarchy")
async def test_hierarchy(test_data: Dict):
    """Test hierarchical agent delegation"""
    agent_type = test_data.get("agent", "understanding")
    query = test_data.get("query", "test query")
    
    try:
        if agent_type == "understanding":
            result = await hierarchical_processor.delegate_to_understanding_agent(query)
        elif agent_type == "action":
            content = test_data.get("content", "test content")
            result = await hierarchical_processor.delegate_to_action_agent(content, query)
        elif agent_type == "delivery":
            results = test_data.get("results", "test results")
            method = test_data.get("method", "email")
            result = await hierarchical_processor.delegate_to_delivery_agent(results, method)
        else:
            return {"status": "error", "message": "Invalid agent type"}
        
        return {"status": "success", "result": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    print("\n✅ Syntra Server Starting...")
    print("🌐 Dashboard: http://localhost:8000/dashboard")
    print("⚡ Workflow automation: Ready")
    print("📂 Monitoring: ~/Downloads\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="warning")