from abc import ABC, abstractmethod
from typing import Dict, Any, Callable
from dataclasses import dataclass
from datetime import datetime

@dataclass
class TriggerEvent:
    """Base event payload for all triggers"""
    trigger_type: str
    timestamp: datetime
    payload: Dict[str, Any]

class BaseTrigger(ABC):
    """Base class for all trigger types"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.enabled = config.get('enabled', True)
        self.callbacks = []
    
    def register_callback(self, callback: Callable[[TriggerEvent], None]):
        """Register a callback to be invoked when trigger fires"""
        self.callbacks.append(callback)
    
    def fire(self, payload: Dict[str, Any]):
        """Fire the trigger with given payload"""
        if not self.enabled:
            return
        
        event = TriggerEvent(
            trigger_type=self.__class__.__name__,
            timestamp=datetime.now(),
            payload=payload
        )
        
        for callback in self.callbacks:
            callback(event)
    
    @abstractmethod
    def start(self):
        """Start monitoring for trigger events"""
        pass
    
    @abstractmethod
    def stop(self):
        """Stop monitoring"""
        pass
