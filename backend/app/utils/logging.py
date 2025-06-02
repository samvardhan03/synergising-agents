import logging
import logging.handlers
import sys
import os
from datetime import datetime
from typing import Optional
import json
from pathlib import Path

from app.config import settings

class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for console output"""
    
    # Color codes
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
        'RESET': '\033[0m'      # Reset
    }
    
    def format(self, record):
        # Add color to levelname
        if hasattr(record, 'levelname'):
            color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
            record.levelname = f"{color}{record.levelname}{self.COLORS['RESET']}"
        
        return super().format(record)

class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging"""
    
    def format(self, record):
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        # Add extra fields
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname',
                          'filename', 'module', 'exc_info', 'exc_text', 'stack_info',
                          'lineno', 'funcName', 'created', 'msecs', 'relativeCreated',
                          'thread', 'threadName', 'processName', 'process', 'getMessage']:
                log_entry[key] = value
        
        return json.dumps(log_entry)

class AgentContextFilter(logging.Filter):
    """Filter to add agent context to log records"""
    
    def __init__(self, agent_type: str = None, workflow_id: str = None):
        super().__init__()
        self.agent_type = agent_type
        self.workflow_id = workflow_id
    
    def filter(self, record):
        if self.agent_type:
            record.agent_type = self.agent_type
        if self.workflow_id:
            record.workflow_id = self.workflow_id
        return True

def setup_logging(
    log_level: str = None,
    log_file: str = None,
    enable_json: bool = False,
    enable_console: bool = True
) -> logging.Logger:
    """Setup application logging configuration"""
    
    # Use settings if parameters not provided
    log_level = log_level or settings.LOG_LEVEL
    log_file = log_file or settings.LOG_FILE
    
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Get root logger
    logger = logging.getLogger("synergistic_agents")
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Console handler
    if enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, log_level.upper()))
        
        if enable_json:
            console_formatter = JSONFormatter()
        else:
            console_formatter = ColoredFormatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
    
    # File handler
    if log_file:
        file_handler = logging.handlers.RotatingFileHandler(
            log_dir / log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(getattr(logging, log_level.upper()))
        
        if enable_json:
            file_formatter = JSONFormatter()
        else:
            file_formatter = logging.Formatter(settings.LOG_FORMAT)
        
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    # Error file handler
    error_handler = logging.handlers.RotatingFileHandler(
        log_dir / "errors.log",
        maxBytes=10*1024*1024,
        backupCount=5
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(
        JSONFormatter() if enable_json else logging.Formatter(settings.LOG_FORMAT)
    )
    logger.addHandler(error_handler)
    
    return logger

def get_logger(name: str, agent_type: str = None, workflow_id: str = None) -> logging.Logger:
    """Get a logger with optional agent context"""
    logger = logging.getLogger(f"synergistic_agents.{name}")
    
    # Add agent context filter if provided
    if agent_type or workflow_id:
        context_filter = AgentContextFilter(agent_type, workflow_id)
        logger.addFilter(context_filter)
    
    return logger

def log_agent_start(logger: logging.Logger, agent_type: str, workflow_id: str, input_data: dict = None):
    """Log agent start with context"""
    logger.info(
        f"Starting {agent_type} agent",
        extra={
            'event': 'agent_start',
            'agent_type': agent_type,
            'workflow_id': workflow_id,
            'input_size': len(str(input_data)) if input_data else 0
        }
    )

def log_agent_complete(logger: logging.Logger, agent_type: str, workflow_id: str, 
                      execution_time: float, result_size: int = 0):
    """Log agent completion with metrics"""
    logger.info(
        f"Completed {agent_type} agent in {execution_time:.2f}s",
        extra={
            'event': 'agent_complete',
            'agent_type': agent_type,
            'workflow_id': workflow_id,
            'execution_time': execution_time,
            'result_size': result_size
        }
    )

def log_agent_error(logger: logging.Logger, agent_type: str, workflow_id: str, 
                   error: Exception, input_data: dict = None):
    """Log agent error with context"""
    logger.error(
        f"Error in {agent_type} agent: {str(error)}",
        extra={
            'event': 'agent_error',
            'agent_type': agent_type,
            'workflow_id': workflow_id,
            'error_type': type(error).__name__,
            'input_data': input_data
        },
        exc_info=True
    )

def log_workflow_start(logger: logging.Logger, workflow_id: str, input_params: dict):
    """Log workflow start"""
    logger.info(
        f"Starting workflow {workflow_id}",
        extra={
            'event': 'workflow_start',
            'workflow_id': workflow_id,
            'input_params': input_params
        }
    )

def log_workflow_complete(logger: logging.Logger, workflow_id: str, total_time: float):
    """Log workflow completion"""
    logger.info(
        f"Workflow {workflow_id} completed in {total_time:.2f}s",
        extra={
            'event': 'workflow_complete',
            'workflow_id': workflow_id,
            'total_time': total_time
        }
    )

def log_api_request(logger: logging.Logger, endpoint: str, method: str, 
                   user_id: str = None, request_size: int = 0):
    """Log API request"""
    logger.info(
        f"{method} {endpoint}",
        extra={
            'event': 'api_request',
            'endpoint': endpoint,
            'method': method,
            'user_id': user_id,
            'request_size': request_size
        }
    )

def log_api_response(logger: logging.Logger, endpoint: str, status_code: int, 
                    response_time: float, response_size: int = 0):
    """Log API response"""
    logger.info(
        f"Response {status_code} for {endpoint} in {response_time:.3f}s",
        extra={
            'event': 'api_response',
            'endpoint': endpoint,
            'status_code': status_code,
            'response_time': response_time,
            'response_size': response_size
        }
    )

def log_data_processing(logger: logging.Logger, operation: str, record_count: int, 
                       processing_time: float):
    """Log data processing operations"""
    logger.info(
        f"Processed {record_count} records for {operation} in {processing_time:.2f}s",
        extra={
            'event': 'data_processing',
            'operation': operation,
            'record_count': record_count,
            'processing_time': processing_time
        }
    )

def log_external_api_call(logger: logging.Logger, api_name: str, endpoint: str, 
                         response_time: float, success: bool):
    """Log external API calls"""
    level = logging.INFO if success else logging.WARNING
    logger.log(
        level,
        f"External API call to {api_name} {'succeeded' if success else 'failed'}",
        extra={
            'event': 'external_api_call',
            'api_name': api_name,
            'endpoint': endpoint,
            'response_time': response_time,
            'success': success
        }
    )

# Performance monitoring decorator
def log_performance(logger: logging.Logger = None):
    """Decorator to log function performance"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            import time
            func_logger = logger or get_logger(func.__module__)
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                func_logger.debug(
                    f"Function {func.__name__} executed in {execution_time:.3f}s",
                    extra={
                        'event': 'function_performance',
                        'function': func.__name__,
                        'execution_time': execution_time,
                        'success': True
                    }
                )
                return result
                
            except Exception as e:
                execution_time = time.time() - start_time
                func_logger.error(
                    f"Function {func.__name__} failed after {execution_time:.3f}s: {str(e)}",
                    extra={
                        'event': 'function_performance',
                        'function': func.__name__,
                        'execution_time': execution_time,
                        'success': False,
                        'error': str(e)
                    }
                )
                raise
        return wrapper
    return decorator

# Initialize logging
main_logger = setup_logging(
    enable_json=settings.DEBUG is False,
    enable_console=True
)
