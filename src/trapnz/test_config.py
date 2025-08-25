"""
Test configuration and utilities for TrapNZ package
"""
import os
from typing import Dict, Any
from uuid import UUID
from .models import Line, Trap, TrapRecord, Project, Organisation, Tag, Coordinates, Meta

def setup_test_environment():
    """Set up test environment variables"""
    os.environ["TEST_MODE"] = "true"
    print("🧪 TEST_MODE enabled")

def create_test_line_data() -> Dict[str, Any]:
    """Create sample test line data"""
    return {
        "uuid": "test-line-2",
        "name": "Test Line 2",
        "project": {
            "uuid": "test-project-2",
            "name": "Test Project 2",
            "location": "Test Location 2",
            "tags": [{"tid": 4, "name": "test2", "uuid": "test-tag-4"}],
            "is_listed": True,
            "share_summary_data": True,
            "curated": False,
            "organisations": [{"name": "Test Org 2", "uuid": "test-org-2"}],
            "contact": "test2@example.com",
            "contact_organisation": "Test Org 2",
            "description": "Test project 2 description",
            "websites": ["https://test2.example.com"],
            "meta": {
                "created": "2025-01-10T00:00:00Z",
                "changed": "2025-01-10T00:00:00Z",
                "owner": {"uuid": "test-owner-2", "username": "testuser2"},
                "nid": 2,
                "originating_system": "test"
            }
        },
        "tags": [{"tid": 5, "name": "line-test2", "uuid": "test-tag-5"}],
        "is_listed": True,
        "share_summary_data": True,
        "curated": False,
        "organisations": [{"name": "Test Org 2", "uuid": "test-org-2"}],
        "contact": "test2@example.com",
        "contact_organisation": "Test Org 2",
        "description": "Test line 2 description",
        "websites": ["https://test2.example.com"],
        "meta": {
            "created": "2025-01-10T00:00:00Z",
            "changed": "2025-01-10T00:00:00Z",
            "owner": {"uuid": "test-owner-2", "username": "testuser2"},
            "nid": 2,
            "originating_system": "test"
        }
    }

def create_test_trap_data() -> Dict[str, Any]:
    """Create sample test trap data"""
    return {
        "uuid": "test-trap-2",
        "name": "Test Trap 2",
        "project": {
            "uuid": "test-project-2",
            "name": "Test Project 2",
            "location": "Test Location 2",
            "tags": [{"tid": 4, "name": "test2", "uuid": "test-tag-4"}],
            "is_listed": True,
            "share_summary_data": True,
            "curated": False,
            "organisations": [{"name": "Test Org 2", "uuid": "test-org-2"}],
            "contact": "test2@example.com",
            "contact_organisation": "Test Org 2",
            "description": "Test project 2 description",
            "websites": ["https://test2.example.com"],
            "meta": {
                "created": "2025-01-10T00:00:00Z",
                "changed": "2025-01-10T00:00:00Z",
                "owner": {"uuid": "test-owner-2", "username": "testuser2"},
                "nid": 2,
                "originating_system": "test"
            }
        },
        "line": {
            "uuid": "test-line-2",
            "name": "Test Line 2",
            "project": {
                "uuid": "test-project-2",
                "name": "Test Project 2",
                "location": "Test Location 2",
                "tags": [{"tid": 4, "name": "test2", "uuid": "test-tag-4"}],
                "is_listed": True,
                "share_summary_data": True,
                "curated": False,
                "organisations": [{"name": "Test Org 2", "uuid": "test-org-2"}],
                "contact": "test2@example.com",
                "contact_organisation": "Test Org 2",
                "description": "Test project 2 description",
                "websites": ["https://test2.example.com"],
                "meta": {
                    "created": "2025-01-10T00:00:00Z",
                    "changed": "2025-01-10T00:00:00Z",
                    "owner": {"uuid": "test-owner-2", "username": "testuser2"},
                    "nid": 2,
                    "originating_system": "test"
                }
            },
            "tags": [{"tid": 5, "name": "line-test2", "uuid": "test-tag-5"}],
            "is_listed": True,
            "share_summary_data": True,
            "curated": False,
            "organisations": [{"name": "Test Org 2", "uuid": "test-org-2"}],
            "contact": "test2@example.com",
            "contact_organisation": "Test Org 2",
            "description": "Test line 2 description",
            "websites": ["https://test2.example.com"],
            "meta": {
                "created": "2025-01-10T00:00:00Z",
                "changed": "2025-01-10T00:00:00Z",
                "owner": {"uuid": "test-owner-2", "username": "testuser2"},
                "nid": 2,
                "originating_system": "test"
            }
        },
        "tags": [{"tid": 6, "name": "trap-test2", "uuid": "test-tag-6"}],
        "is_listed": True,
        "share_summary_data": True,
        "curated": False,
        "organisations": [{"name": "Test Org 2", "uuid": "test-org-2"}],
        "contact": "test2@example.com",
        "contact_organisation": "Test Org 2",
        "description": "Test trap 2 description",
        "websites": ["https://test2.example.com"],
        "trap_type": "DOC250",
        "coordinates": {"coordinates": [174.1, -41.1], "bbox": [174.0, -41.2, 174.2, -41.0]},
        "elevation": 150.0,
        "last_check": "2025-01-10T13:00:00Z",
        "last_reset": "2025-01-10T11:00:00Z",
        "run_time": 10800,
        "battery_voltage": 11.8,
        "bar_state": "Set",
        "eye_1": 1,
        "eye_2": 1,
        "ambient_1": 22,
        "ambient_2": 22,
        "life_cycles": 75,
        "all_cycles": 150,
        "cycles_by_eye": 38,
        "bait_cycles": 15,
        "possums": 8,
        "days_between_baiting": 25,
        "bait_run_time_seconds": 5400,
        "set_state": True,
        "runon": 1,
        "prefeed_days": 2,
        "temp_celsius": 19.5,
        "hard_reboots": 1,
        "last_error": "None",
        "last_error_level": "Success",
        "last_reboot_reason": "Scheduled",
        "event": "Heartbeat",
        "rcoms_reason": "NORMAL",
        "long_log": "Test log entry 2",
        "short_log": "Test2",
        "diary": "Test diary entry 2",
        "eeprom": "Test eeprom data 2",
        "rtcbu": "Test rtcbu data 2",
        "extended": {"test_key2": "test_value2"},
        "set_status": "green",
        "battery_health": "green",
        "eye_1_health": "green",
        "eye_2_health": "green",
        "reboot_reason_health": "green",
        "overall_health": "green",
        "trap_status_reasons": ["not set"],
        "meta": {
            "created": "2025-01-10T00:00:00Z",
            "changed": "2025-01-10T00:00:00Z",
            "owner": {"uuid": "test-owner-2", "username": "testuser2"},
            "nid": 2,
            "originating_system": "test"
        }
    }

def create_test_record_data() -> Dict[str, Any]:
    """Create sample test trap record data"""
    return {
        "uuid": "test-record-2",
        "trap": create_test_trap_data(),
        "project": {
            "uuid": "test-project-2",
            "name": "Test Project 2",
            "location": "Test Location 2",
            "tags": [{"tid": 4, "name": "test2", "uuid": "test-tag-4"}],
            "is_listed": True,
            "share_summary_data": True,
            "curated": False,
            "organisations": [{"name": "Test Org 2", "uuid": "test-org-2"}],
            "contact": "test2@example.com",
            "contact_organisation": "Test Org 2",
            "description": "Test project 2 description",
            "websites": ["https://test2.example.com"],
            "meta": {
                "created": "2025-01-10T00:00:00Z",
                "changed": "2025-01-10T00:00:00Z",
                "owner": {"uuid": "test-owner-2", "username": "testuser2"},
                "nid": 2,
                "originating_system": "test"
            }
        },
        "line": {
            "uuid": "test-line-2",
            "name": "Test Line 2",
            "project": {
                "uuid": "test-project-2",
                "name": "Test Project 2",
                "location": "Test Location 2",
                "tags": [{"tid": 4, "name": "test2", "uuid": "test-tag-4"}],
                "is_listed": True,
                "share_summary_data": True,
                "curated": False,
                "organisations": [{"name": "Test Org 2", "uuid": "test-org-2"}],
                "contact": "test2@example.com",
                "contact_organisation": "Test Org 2",
                "description": "Test project 2 description",
                "websites": ["https://test2.example.com"],
                "meta": {
                    "created": "2025-01-10T00:00:00Z",
                    "changed": "2025-01-10T00:00:00Z",
                    "owner": {"uuid": "test-owner-2", "username": "testuser2"},
                    "nid": 2,
                    "originating_system": "test"
                }
            },
            "tags": [{"tid": 5, "name": "line-test2", "uuid": "test-tag-5"}],
            "is_listed": True,
            "share_summary_data": True,
            "curated": False,
            "organisations": [{"name": "Test Org 2", "uuid": "test-org-2"}],
            "contact": "test2@example.com",
            "contact_organisation": "Test Org 2",
            "description": "Test line 2 description",
            "websites": ["https://test2.example.com"],
            "meta": {
                "created": "2025-01-10T00:00:00Z",
                "changed": "2025-01-10T00:00:00Z",
                "owner": {"uuid": "test-owner-2", "username": "testuser2"},
                "nid": 2,
                "originating_system": "test"
            }
        },
        "date": "2025-01-10T13:00:00Z",
        "event": "Heartbeat",
        "status": "Set",
        "rssi": -42.0,
        "battery_voltage": 11.8,
        "snr": 18.0,
        "sensor_id": "test-sensor-2",
        "sensor_provider": "test-provider-2",
        "meta": {
            "created": "2025-01-10T13:00:00Z",
            "changed": "2025-01-10T13:00:00Z",
            "owner": {"uuid": "test-owner-2", "username": "testuser2"},
            "nid": 2,
            "originating_system": "test"
        }
    }
