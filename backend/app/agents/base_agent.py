from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import time
import asyncio
from datetime import datetime
import uuid

from app.models.data_models import (
    AgentType, WorkflowStatus, AgentResult, 
    WebSocketMessage, ProgressUpdate
)
from app.utils.logging import get_logger, log_performance
from app.config import settings

class BaseAgent(ABC):
    """Base class for all agents in the synergistic system"""
    
    def __init__(self, agent_type: AgentType, workflow_id: str = None):
        self.agent_type = agent_type
        self.workflow_id = workflow_id or str(uuid.uuid4())
        self.logger = get_logger(f"agent.{agent_type.value}", agent_type.value, self.workflow_id)
        self.status = WorkflowStatus.PENDING
        self.result_data: Optional[Dict[str, Any]] = None
        self.error_message: Optional[str] = None
        self.execution_time: Optional[float] = None
        self.progress_callbacks: List[callable] = []
        
        # Agent-specific configuration
        self.config = self._load_agent_config()
        
        # Performance metrics
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        
        self.logger.info(f"Initialized {agent_type.value} agent for workflow {self.workflow_id}")
    
    def _load_agent_config(self) -> Dict[str, Any]:
        """Load agent-specific configuration"""
        base_config = {
            "timeout": settings.WORKFLOW_TIMEOUT,
            "max_retries": 3,
            "retry_delay": 1.0,
            "enable_caching": settings.ENABLE_CACHING,
            "cache_ttl": settings.CACHE_TTL
        }
        
        # Agent-specific configurations
        agent_configs = {
            AgentType.FORECASTING: {
                "model_type": settings.FORECASTING_MODEL,
                "confidence_level": 0.95,
                "max_forecast_days": 365
            },
            AgentType.NEWS: {
                "max_articles": 50,
                "sources": settings.NEWS_SOURCES,
                "min_relevance": 0.5
            },
            AgentType.SIMULATION: {
                "iterations": settings.SIMULATION_ITERATIONS,
                "confidence_level": 0.95,
                "max_scenarios": 10
            },
            AgentType.SUMMARY: {
                "max_slides": 20,
                "include_charts": True,
                "executive_summary": True
            }
        }
        
        base_config.update(agent_configs.get(self.agent_type, {}))
        return base_config
    
    def add_progress_callback(self, callback: callable):
        """Add a callback function for progress updates"""
        self.progress_callbacks.append(callback)
    
    def _notify_progress(self, progress: float, message: str, step: str = None):
        """Notify all registered callbacks about progress"""
        progress_update = ProgressUpdate(
            workflow_id=self.workflow_id,
            agent_type=self.agent_type,
            progress_percentage=progress,
            status_message=message,
            current_step=step
        )
        for callback in self.progress_callbacks:
            callback(progress_update)
