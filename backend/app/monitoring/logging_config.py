"""
Structured Logging Configuration
Phase 9: Observability
"""
import logging
import json
import sys
from datetime import datetime
from typing import Dict, Any
from pythonjsonlogger import jsonlogger


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """
    Custom JSON formatter for structured logging
    
    Adds timestamp, request_id, and other context
    """
    
    def add_fields(self, log_record: Dict, record: logging.LogRecord, message_dict: Dict):
        super().add_fields(log_record, record, message_dict)
        
        # Add timestamp
        log_record['timestamp'] = datetime.utcnow().isoformat()
        log_record['level'] = record.levelname
        log_record['logger'] = record.name
        
        # Add request context if available
        if hasattr(record, 'request_id'):
            log_record['request_id'] = record.request_id
        
        if hasattr(record, 'user_id'):
            log_record['user_id'] = record.user_id
        
        if hasattr(record, 'organization_id'):
            log_record['organization_id'] = record.organization_id
        
        # Add extra fields
        if hasattr(record, 'extra'):
            log_record.update(record.extra)


def setup_logging(log_level: str = "INFO", json_logs: bool = True):
    """
    Setup application logging
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_logs: Use JSON format for logs
    """
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Remove existing handlers
    root_logger.handlers = []
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level.upper()))
    
    if json_logs:
        # JSON formatter
        formatter = CustomJsonFormatter(
            '%(timestamp)s %(level)s %(name)s %(message)s'
        )
    else:
        # Standard formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Application logger
    app_logger = logging.getLogger('app')
    app_logger.setLevel(getattr(logging, log_level.upper()))
    
    return app_logger


class ContextLogger:
    """
    Logger with request context
    
    Automatically adds request_id, user_id, etc. to all log messages
    """
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.context: Dict[str, Any] = {}
    
    def set_context(self, **kwargs):
        """Set logging context"""
        self.context.update(kwargs)
    
    def clear_context(self):
        """Clear logging context"""
        self.context = {}
    
    def _log(self, level: int, message: str, **kwargs):
        """Log with context"""
        extra = {**self.context, **kwargs}
        self.logger.log(level, message, extra={'extra': extra})
    
    def debug(self, message: str, **kwargs):
        """Debug log"""
        self._log(logging.DEBUG, message, **kwargs)
    
    def info(self, message: str, **kwargs):
        """Info log"""
        self._log(logging.INFO, message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Warning log"""
        self._log(logging.WARNING, message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Error log"""
        self._log(logging.ERROR, message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        """Critical log"""
        self._log(logging.CRITICAL, message, **kwargs)


# Create application logger
app_logger = setup_logging(log_level="INFO", json_logs=True)
context_logger = ContextLogger(app_logger)


# Audit logging
class AuditLogger:
    """
    Dedicated audit logger for security events
    
    Logs all security-relevant actions
    """
    
    def __init__(self):
        self.logger = logging.getLogger('audit')
        self.logger.setLevel(logging.INFO)
    
    def log_auth_success(self, user_email: str, ip_address: str):
        """Log successful authentication"""
        self.logger.info(
            "Authentication successful",
            extra={
                'event_type': 'auth_success',
                'user_email': user_email,
                'ip_address': ip_address
            }
        )
    
    def log_auth_failure(self, user_email: str, ip_address: str, reason: str):
        """Log failed authentication"""
        self.logger.warning(
            "Authentication failed",
            extra={
                'event_type': 'auth_failure',
                'user_email': user_email,
                'ip_address': ip_address,
                'reason': reason
            }
        )
    
    def log_permission_denied(
        self,
        user_id: int,
        resource_type: str,
        resource_id: str,
        required_permission: str
    ):
        """Log permission denied"""
        self.logger.warning(
            "Permission denied",
            extra={
                'event_type': 'permission_denied',
                'user_id': user_id,
                'resource_type': resource_type,
                'resource_id': resource_id,
                'required_permission': required_permission
            }
        )
    
    def log_data_access(
        self,
        user_id: int,
        resource_type: str,
        resource_id: str,
        action: str
    ):
        """Log data access"""
        self.logger.info(
            f"Data {action}",
            extra={
                'event_type': 'data_access',
                'user_id': user_id,
                'resource_type': resource_type,
                'resource_id': resource_id,
                'action': action
            }
        )
    
    def log_configuration_change(
        self,
        user_id: int,
        change_type: str,
        details: Dict
    ):
        """Log configuration change"""
        self.logger.info(
            "Configuration changed",
            extra={
                'event_type': 'config_change',
                'user_id': user_id,
                'change_type': change_type,
                'details': details
            }
        )


# Create audit logger instance
audit_logger = AuditLogger()
