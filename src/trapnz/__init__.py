"""
Trap.NZ API integration package
"""

from .models import (
    Line, Trap, TrapRecord, Project, Organisation, Tag, 
    Coordinates, Meta, PaginatedResponse, LineListResponse,
    TrapListResponse, TrapRecordListResponse, Volunteer
)

from .database import TrapNZDatabase, TrapNZAPIFacade
from .logging_config import setup_logging, setup_default_logging, get_logger
from .test_config import setup_test_environment, create_test_line_data, create_test_trap_data, create_test_record_data
from .agent_tools import TrapNZAgentTools, create_agent_tools

__version__ = "0.1.0"
__all__ = [
    "Line", "Trap", "TrapRecord", "Project", "Organisation", 
    "Tag", "Coordinates", "Meta", "PaginatedResponse", 
    "LineListResponse", "TrapListResponse", "TrapRecordListResponse",
    "TrapNZDatabase", "TrapNZAPIFacade", "TrapNZAgentTools", "create_agent_tools",
    "setup_logging", "setup_default_logging", "get_logger",
    "setup_test_environment", "create_test_line_data", "create_test_trap_data", "create_test_record_data"
]
