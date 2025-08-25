"""
OpenAI Agent Tools for Trap.NZ Database Operations
Provides tool schemas and functions for AI agents to interact with trap data
"""
from typing import List, Dict, Any, Optional
from uuid import UUID
from .database import TrapNZDatabase
from .models import Line, Trap, TrapRecord
from .logging_config import get_logger

# Note: This implementation uses explicit tool schemas rather than decorators
# The OpenAI SDK @tool decorator is typically used with OpenAI's Assistant API
# For function calling with Chat Completions API, explicit schemas are more appropriate

logger = get_logger(__name__)

class TrapNZAgentTools:
    """Collection of OpenAI-ready agent tools for Trap.NZ operations"""
    
    def __init__(self, db: TrapNZDatabase):
        self.db = db
    
    def get_tool_schemas(self) -> List[Dict[str, Any]]:
        """Return all available tool schemas for OpenAI agents"""
        return [
            {
                "type": "function",
                "function": {
                    "name": "get_all_lines",
                    "description": "Retrieve all trap lines from the database. Returns a list of all lines with their projects, tags, and metadata.",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_all_traps",
                    "description": "Retrieve all traps from the database. Returns a list of all traps with their line information, health status, and performance metrics. Useful for analysis of traps such as which traps need checking.",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_all_trap_records",
                    "description": "Retrieve all trap records from the database. Returns the latest record for each trap with sensor data and status information.",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_lines_by_uuids",
                    "description": "Retrieve specific trap lines by their UUIDs. Returns detailed information about the requested lines including projects, tags, and metadata.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "line_uuids": {
                                "type": "array",
                                "items": {
                                    "type": "string",
                                    "description": "UUID of the trap line"
                                },
                                "description": "List of line UUIDs to retrieve"
                            }
                        },
                        "required": ["line_uuids"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_traps_by_line_uuids",
                    "description": "Retrieve all traps within specific lines by line UUIDs. Returns traps with their health status, performance metrics, and location data.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "line_uuids": {
                                "type": "array",
                                "items": {
                                    "type": "string",
                                    "description": "UUID of the trap line"
                                },
                                "description": "List of line UUIDs to retrieve traps from"
                                }
                            },
                        "required": ["line_uuids"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_latest_records_for_traps",
                    "description": "Retrieve the latest record for each specified trap. Returns sensor data, status, and performance metrics for each trap.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "trap_uuids": {
                                "type": "array",
                                "items": {
                                    "type": "string",
                                    "description": "UUID of the trap"
                                },
                                "description": "List of trap UUIDs to retrieve records for"
                            }
                        },
                        "required": ["trap_uuids"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_trap_records_by_trap",
                    "description": "Retrieve multiple trap records for a specific trap, ordered by date. Useful for analyzing trap performance over time.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "trap_uuid": {
                                "type": "string",
                                "description": "UUID of the trap to get records for"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of records to retrieve (default: 100)",
                                "default": 100
                            }
                        },
                        "required": ["trap_uuid"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "search_traps_by_status",
                    "description": "Search for traps by their health status. Returns traps matching the specified status criteria.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "status": {
                                "type": "string",
                                "enum": ["green", "amber", "red", "unknown"],
                                "description": "Health status to search for"
                            }
                        },
                        "required": ["status"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "search_traps_by_type",
                    "description": "Search for traps by their type (e.g., DOC200, DOC250). Returns all traps of the specified type.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "trap_type": {
                                "type": "string",
                                "description": "Type of trap to search for (e.g., DOC200, DOC250)"
                            }
                        },
                        "required": ["trap_type"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_trap_performance_summary",
                    "description": "Get a performance summary for a specific trap including catch rates, battery health, and operational statistics. Use this to identify busy traps that might need checking more often",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "trap_uuid": {
                                "type": "string",
                                "description": "UUID of the trap to get performance summary for"
                            }
                        },
                        "required": ["trap_uuid"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_line_summary",
                    "description": "Get a summary of a specific line including trap count, overall health, and recent activity.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "line_uuid": {
                                "type": "string",
                                "description": "UUID of the line to get summary for"
                            }
                        },
                        "required": ["line_uuid"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "update_volunteer",
                    "description": "Creates or Updates a volunteer and their preferences",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            }
        ]
    
    def get_tool_functions(self) -> Dict[str, callable]:
        """Return all available tool functions for OpenAI agents"""
        return {
            "get_all_lines": self.get_all_lines,
            "get_all_traps": self.get_all_traps,
            "get_all_trap_records": self.get_all_trap_records,
            "get_lines_by_uuids": self.get_lines_by_uuids,
            "get_traps_by_line_uuids": self.get_traps_by_line_uuids,
            "get_latest_records_for_traps": self.get_latest_records_for_traps,
            "get_trap_records_by_trap": self.get_trap_records_by_trap,
            "search_traps_by_status": self.search_traps_by_status,
            "search_traps_by_type": self.search_traps_by_type,
            "get_trap_performance_summary": self.get_trap_performance_summary,
            "get_line_summary": self.get_line_summary
        }
    
    def get_all_lines(self) -> Dict[str, Any]:
        """Agent tool: Get all lines from database"""
        try:
            lines = self.db.get_all_lines()
            return {
                "success": True,
                "data": {
                    "total_lines": len(lines),
                    "lines": [
                        {
                            "uuid": str(line.uuid),
                            "name": line.name,
                            "project_name": line.project.name if line.project else "Unknown",
                            "location": line.project.location if line.project else "Unknown",
                            "tags": [tag.name for tag in line.tags],
                            "is_listed": line.is_listed,
                            "curated": line.curated,
                            "description": line.description or "No description"
                        }
                        for line in lines
                    ]
                }
            }
        except Exception as e:
            logger.error(f"Error in get_all_lines: {e}")
            return {"success": False, "error": str(e)}
    
    def get_all_traps(self) -> Dict[str, Any]:
        """Agent tool: Get all traps from database. Useful for analysis of traps such as
        which traps need checking"""
        try:
            traps = self.db.get_all_traps()
            return {
                "success": True,
                "data": {
                    "total_traps": len(traps),
                    "traps": [
                        {
                            "uuid": str(trap.uuid),
                            "name": trap.name,
                            "trap_type": trap.trap_type,
                            "line_name": trap.line.name if trap.line else "Unknown",
                            "project_name": trap.project.name if trap.project else "Unknown",
                            "overall_health": trap.overall_health,
                            "battery_voltage": trap.battery_voltage,
                            "possums": trap.possums,
                            "last_check": trap.last_check.isoformat() if trap.last_check else None,
                            "coordinates": trap.coordinates.coordinates if trap.coordinates else None
                        }
                        for trap in traps
                    ]
                }
            }
        except Exception as e:
            logger.error(f"Error in get_all_traps: {e}")
            return {"success": False, "error": str(e)}
    
    def get_all_trap_records(self) -> Dict[str, Any]:
        """Agent tool: Get all trap records from database"""
        try:
            records = self.db.get_all_trap_records()
            return {
                "success": True,
                "data": {
                    "total_records": len(records),
                    "records": [
                        {
                            "uuid": str(record.uuid),
                            "trap_name": record.trap.name if record.trap else "Unknown",
                            "line_name": record.line.name if record.line else "Unknown",
                            "event": record.event,
                            "status": record.status,
                            "date": record.date.isoformat() if record.date else None,
                            "battery_voltage": record.battery_voltage,
                            "rssi": record.rssi
                        }
                        for record in records
                    ]
                }
            }
        except Exception as e:
            logger.error(f"Error in get_all_trap_records: {e}")
            return {"success": False, "error": str(e)}
    
    def get_lines_by_uuids(self, line_uuids: List[str]) -> Dict[str, Any]:
        """Agent tool: Get specific lines by UUIDs"""
        try:
            # Convert string UUIDs to UUID objects
            uuids = [UUID(uuid_str) for uuid_str in line_uuids]
            lines = self.db.get_lines_by_uuids(uuids)
            
            return {
                "success": True,
                "data": {
                    "requested_lines": len(line_uuids),
                    "found_lines": len(lines),
                    "lines": [
                        {
                            "uuid": str(line.uuid),
                            "name": line.name,
                            "project_name": line.project.name if line.project else "Unknown",
                            "location": line.project.location if line.project else "Unknown",
                            "tags": [tag.name for tag in line.tags],
                            "is_listed": line.is_listed,
                            "curated": line.curated,
                            "description": line.description or "No description",
                            "organisations": [org.name for org in line.organisations]
                        }
                        for line in lines
                    ]
                }
            }
        except Exception as e:
            logger.error(f"Error in get_lines_by_uuids: {e}")
            return {"success": False, "error": str(e)}
    
    def get_traps_by_line_uuids(self, line_uuids: List[str]) -> Dict[str, Any]:
        """Agent tool: Get traps by line UUIDs"""
        try:
            # Convert string UUIDs to UUID objects
            uuids = [UUID(uuid_str) for uuid_str in line_uuids]
            traps = self.db.get_traps_by_line_uuids(uuids)
            
            return {
                "success": True,
                "data": {
                    "requested_lines": len(line_uuids),
                    "total_traps": len(traps),
                    "traps": [
                        {
                            "uuid": str(trap.uuid),
                            "name": trap.name,
                            "trap_type": trap.trap_type,
                            "line_name": trap.line.name if trap.line else "Unknown",
                            "project_name": trap.project.name if trap.project else "Unknown",
                            "overall_health": trap.overall_health,
                            "battery_voltage": trap.battery_voltage,
                            "possums": trap.possums,
                            "last_check": trap.last_check.isoformat() if trap.last_check else None,
                            "coordinates": trap.coordinates.coordinates if trap.coordinates else None
                        }
                        for trap in traps
                    ]
                }
            }
        except Exception as e:
            logger.error(f"Error in get_traps_by_line_uuids: {e}")
            return {"success": False, "error": str(e)}
    
    def get_latest_records_for_traps(self, trap_uuids: List[str]) -> Dict[str, Any]:
        """Agent tool: Get latest records for specific traps"""
        try:
            # Convert string UUIDs to UUID objects
            uuids = [UUID(uuid_str) for uuid_str in trap_uuids]
            records = self.db.get_latest_records_for_traps(uuids)
            
            return {
                "success": True,
                "data": {
                    "requested_traps": len(trap_uuids),
                    "found_records": len(records),
                    "records": [
                        {
                            "uuid": str(record.uuid),
                            "trap_name": record.trap.name if record.trap else "Unknown",
                            "line_name": record.line.name if record.line else "Unknown",
                            "event": record.event,
                            "status": record.status,
                            "date": record.date.isoformat() if record.date else None,
                            "battery_voltage": record.battery_voltage,
                            "rssi": record.rssi
                        }
                        for record in records
                    ]
                }
            }
        except Exception as e:
            logger.error(f"Error in get_latest_records_for_traps: {e}")
            return {"success": False, "error": str(e)}
    
    def get_trap_records_by_trap(self, trap_uuid: str, limit: int = 100) -> Dict[str, Any]:
        """Agent tool: Get multiple records for a specific trap"""
        try:
            uuid_obj = UUID(trap_uuid)
            records = self.db.get_trap_records_by_trap(uuid_obj, limit)
            
            return {
                "success": True,
                "data": {
                    "trap_uuid": trap_uuid,
                    "total_records": len(records),
                    "limit": limit,
                    "records": [
                        {
                            "uuid": str(record.uuid),
                            "event": record.event,
                            "status": record.status,
                            "date": record.date.isoformat() if record.date else None,
                            "battery_voltage": record.battery_voltage,
                            "rssi": record.rssi,
                            "snr": record.snr
                        }
                        for record in records
                    ]
                }
            }
        except Exception as e:
            logger.error(f"Error in get_trap_records_by_trap: {e}")
            return {"success": False, "error": str(e)}
    
    def search_traps_by_status(self, status: str) -> Dict[str, Any]:
        """Agent tool: Search traps by health status"""
        try:
            all_traps = self.db.get_all_traps()
            filtered_traps = [
                trap for trap in all_traps 
                if trap.overall_health and trap.overall_health.lower() == status.lower()
            ]
            
            return {
                "success": True,
                "data": {
                    "status": status,
                    "total_traps": len(filtered_traps),
                    "traps": [
                        {
                            "uuid": str(trap.uuid),
                            "name": trap.name,
                            "trap_type": trap.trap_type,
                            "line_name": trap.line.name if trap.line else "Unknown",
                            "overall_health": trap.overall_health,
                            "battery_voltage": trap.battery_voltage,
                            "possums": trap.possums,
                            "last_check": trap.last_check.isoformat() if trap.last_check else None
                        }
                        for trap in filtered_traps
                    ]
                }
            }
        except Exception as e:
            logger.error(f"Error in search_traps_by_status: {e}")
            return {"success": False, "error": str(e)}
    
    def search_traps_by_type(self, trap_type: str) -> Dict[str, Any]:
        """Agent tool: Search traps by type"""
        try:
            all_traps = self.db.get_all_traps()
            filtered_traps = [
                trap for trap in all_traps 
                if trap.trap_type and trap_type.lower() in trap.trap_type.lower()
            ]
            
            return {
                "success": True,
                "data": {
                    "trap_type": trap_type,
                    "total_traps": len(filtered_traps),
                    "traps": [
                        {
                            "uuid": str(trap.uuid),
                            "name": trap.name,
                            "trap_type": trap.trap_type,
                            "line_name": trap.line.name if trap.line else "Unknown",
                            "overall_health": trap.overall_health,
                            "battery_voltage": trap.battery_voltage,
                            "possums": trap.possums,
                            "last_check": trap.last_check.isoformat() if trap.last_check else None
                        }
                        for trap in filtered_traps
                    ]
                }
            }
        except Exception as e:
            logger.error(f"Error in search_traps_by_type: {e}")
            return {"success": False, "error": str(e)}
    
    def get_trap_performance_summary(self, trap_uuid: str) -> Dict[str, Any]:
        """Agent tool: Get performance summary for a specific trap. Use this
        to identify busy traps that might need checking more often"""
        try:
            uuid_obj = UUID(trap_uuid)
            records = self.db.get_trap_records_by_trap(uuid_obj, limit=100)
            
            if not records:
                return {"success": False, "error": "No records found for this trap"}
            
            # Calculate performance metrics
            total_possums = sum(1 for record in records if record.event and "possum" in record.event.lower())
            battery_readings = [record.battery_voltage for record in records if record.battery_voltage]
            recent_records = sorted(records, key=lambda x: x.date, reverse=True)[:10]
            
            return {
                "success": True,
                "data": {
                    "trap_uuid": trap_uuid,
                    "total_records": len(records),
                    "performance_metrics": {
                        "total_possums": total_possums,
                        "average_battery": sum(battery_readings) / len(battery_readings) if battery_readings else 0,
                        "min_battery": min(battery_readings) if battery_readings else 0,
                        "max_battery": max(battery_readings) if battery_readings else 0,
                        "recent_activity": len(recent_records)
                    },
                    "recent_events": [
                        {
                            "date": record.date.isoformat() if record.date else None,
                            "event": record.event,
                            "status": record.status,
                            "battery_voltage": record.battery_voltage
                        }
                        for record in recent_records
                    ]
                }
            }
        except Exception as e:
            logger.error(f"Error in get_trap_performance_summary: {e}")
            return {"success": False, "error": str(e)}
    
    def get_line_summary(self, line_uuid: str) -> Dict[str, Any]:
        """Agent tool: Get summary for a specific line"""
        try:
            uuid_obj = UUID(line_uuid)
            line_data = self.db.get_lines_by_uuids([uuid_obj])
            
            if not line_data:
                return {"success": False, "error": "Line not found"}
            
            line = line_data[0]
            traps = self.db.get_traps_by_line_uuids([uuid_obj])
            
            # Calculate line statistics
            total_traps = len(traps)
            healthy_traps = sum(1 for trap in traps if trap.overall_health == "green")
            total_possums = sum(trap.possums for trap in traps if trap.possums)
            
            return {
                "success": True,
                "data": {
                    "line_uuid": line_uuid,
                    "line_name": line.name,
                    "project_name": line.project.name if line.project else "Unknown",
                    "location": line.project.location if line.project else "Unknown",
                    "summary": {
                        "total_traps": total_traps,
                        "healthy_traps": healthy_traps,
                        "health_percentage": (healthy_traps / total_traps * 100) if total_traps > 0 else 0,
                        "total_possums": total_possums
                    },
                    "traps": [
                        {
                            "uuid": str(trap.uuid),
                            "name": trap.name,
                            "trap_type": trap.trap_type,
                            "overall_health": trap.overall_health,
                            "battery_voltage": trap.battery_voltage,
                            "possums": trap.possums
                        }
                        for trap in traps
                    ]
                }
            }
        except Exception as e:
            logger.error(f"Error in get_line_summary: {e}")
            return {"success": False, "error": str(e)}


def create_agent_tools(db: TrapNZDatabase) -> TrapNZAgentTools:
    """Factory function to create agent tools instance"""
    return TrapNZAgentTools(db)
