from typing import Dict, List, Any
from core.trigger_base import BaseTrigger, TriggerEvent
from triggers.file_trigger import FileTrigger
from triggers.browser_trigger import BrowserTrigger

class TriggerManager:
    """Manages all triggers and routes events to workflows"""
    
    def __init__(self):
        self.triggers: List[BaseTrigger] = []
        self.trigger_map = {
            "file_watcher": FileTrigger,
            "browser_event": BrowserTrigger
        }
    
    def add_trigger(self, trigger_config: Dict[str, Any]) -> BaseTrigger:
        """Create and register a trigger from config"""
        trigger_type = trigger_config.get("type")
        
        if trigger_type not in self.trigger_map:
            raise ValueError(f"Unknown trigger type: {trigger_type}")
        
        trigger_class = self.trigger_map[trigger_type]
        trigger = trigger_class(trigger_config)
        self.triggers.append(trigger)
        
        return trigger
    
    def start_all(self):
        """Start all registered triggers"""
        for trigger in self.triggers:
            trigger.start()
    
    def stop_all(self):
        """Stop all triggers"""
        for trigger in self.triggers:
            trigger.stop()
    
    def on_trigger_event(self, callback):
        """Register a global callback for all trigger events"""
        for trigger in self.triggers:
            trigger.register_callback(callback)
