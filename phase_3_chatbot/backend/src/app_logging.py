"""
Logging Configuration for Todo AI Chatbot
Handles logging for MCP tool usage and system events
"""

import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional

# Configure the root logger for the application
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('todo_chatbot.log')
    ]
)

# Create loggers for different components
app_logger = logging.getLogger('todo_app')
mcp_logger = logging.getLogger('mcp_tools')
chat_logger = logging.getLogger('chat_interface')
auth_logger = logging.getLogger('authentication')


class StructuredLogger:
    """
    Provides structured logging for better observability
    """

    def __init__(self, name: str):
        self.logger = logging.getLogger(name)

    def log_event(self, event_type: str, level: str, **kwargs):
        """
        Log an event with structured data

        Args:
            event_type: Type of event (e.g., 'tool_call', 'user_action', 'error')
            level: Logging level ('info', 'warning', 'error', 'critical')
            **kwargs: Additional data to log
        """
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': event_type,
            'level': level.upper(),
            **kwargs
        }

        getattr(self.logger, level.lower())(json.dumps(log_data))

    def log_tool_call(self, tool_name: str, user_id: str, success: bool,
                     duration_ms: Optional[float] = None, error: Optional[str] = None):
        """
        Log MCP tool usage

        Args:
            tool_name: Name of the MCP tool called
            user_id: ID of the user who initiated the call
            success: Whether the tool call was successful
            duration_ms: Duration of the tool call in milliseconds
            error: Error message if the call failed
        """
        self.log_event(
            event_type='mcp_tool_call',
            level='info' if success else 'error',
            tool_name=tool_name,
            user_id=user_id,
            success=success,
            duration_ms=duration_ms,
            error=error
        )

    def log_user_interaction(self, user_id: str, message: str, intent: str,
                           response: str, channel: str = 'chat'):
        """
        Log user interaction with the system

        Args:
            user_id: ID of the user
            message: Original user message
            intent: Recognized intent
            response: System response
            channel: Channel of interaction (chat, voice, etc.)
        """
        self.log_event(
            event_type='user_interaction',
            level='info',
            user_id=user_id,
            message=message,
            intent=intent,
            response=response,
            channel=channel
        )

    def log_error(self, error: Exception, context: str = "", user_id: Optional[str] = None):
        """
        Log an error with context

        Args:
            error: The exception that occurred
            context: Context where the error occurred
            user_id: User ID if applicable
        """
        self.log_event(
            event_type='error',
            level='error',
            error_type=type(error).__name__,
            error_message=str(error),
            context=context,
            user_id=user_id
        )


# Create structured loggers for different components
structured_app_logger = StructuredLogger('todo_app')
structured_mcp_logger = StructuredLogger('mcp_tools')
structured_chat_logger = StructuredLogger('chat_interface')
structured_auth_logger = StructuredLogger('authentication')


def log_mcp_tool_usage(tool_name: str, user_id: str, success: bool,
                      duration_ms: Optional[float] = None, error: Optional[str] = None):
    """
    Convenience function to log MCP tool usage

    Args:
        tool_name: Name of the MCP tool called
        user_id: ID of the user who initiated the call
        success: Whether the tool call was successful
        duration_ms: Duration of the tool call in milliseconds
        error: Error message if the call failed
    """
    structured_mcp_logger.log_tool_call(tool_name, user_id, success, duration_ms, error)


def log_user_interaction(user_id: str, message: str, intent: str,
                        response: str, channel: str = 'chat'):
    """
    Convenience function to log user interaction

    Args:
        user_id: ID of the user
        message: Original user message
        intent: Recognized intent
        response: System response
        channel: Channel of interaction (chat, voice, etc.)
    """
    structured_chat_logger.log_user_interaction(user_id, message, intent, response, channel)


def log_error(error: Exception, context: str = "", user_id: Optional[str] = None):
    """
    Convenience function to log an error with context

    Args:
        error: The exception that occurred
        context: Context where the error occurred
        user_id: User ID if applicable
    """
    structured_app_logger.log_error(error, context, user_id)