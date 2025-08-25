"""
SQLite database operations for TrapNZ data
"""
import sqlite3
import json
import logging
import os
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID
import httpx
from .models import Line, Trap, TrapRecord, Project, Organisation, Tag, Coordinates, Meta, Volunteer

# Set up logging
logger = logging.getLogger(__name__)

class TrapNZAPIFacade:
    """Facade for Trap.NZ API calls with test mode support"""
    
    def __init__(self, api_base_url: str = "https://api2.trap.nz"):
        self.api_base_url = api_base_url
        self.test_mode = os.getenv("TEST_MODE", "false").lower() == "true"
        
        if self.test_mode:
            logger.info("🧪 TEST_MODE enabled - using canned data instead of real API calls")
            self._init_test_data()
    
    def _init_test_data(self):
        """Initialize canned test data"""
        # Sample test data - you can expand this with more realistic data
        self.test_lines = {
            "test-line-1": {
                "uuid": "test-line-1",
                "name": "Test Line 1",
                "project": {
                    "uuid": "test-project-1",
                    "name": "Test Project 1",
                    "location": "Test Location",
                    "tags": [{"tid": 1, "name": "test", "uuid": "test-tag-1"}],
                    "is_listed": True,
                    "share_summary_data": True,
                    "curated": False,
                    "organisations": [{"name": "Test Org", "uuid": "test-org-1"}],
                    "contact": "test@example.com",
                    "contact_organisation": "Test Org",
                    "description": "Test project description",
                    "websites": ["https://test.example.com"],
                    "meta": {
                        "created": "2025-01-10T00:00:00Z",
                        "changed": "2025-01-10T00:00:00Z",
                        "owner": {"uuid": "test-owner", "username": "testuser"},
                        "nid": 1,
                        "originating_system": "test"
                    }
                },
                "tags": [{"tid": 2, "name": "line-test", "uuid": "test-tag-2"}],
                "is_listed": True,
                "share_summary_data": True,
                "curated": False,
                "organisations": [{"name": "Test Org", "uuid": "test-org-1"}],
                "contact": "test@example.com",
                "contact_organisation": "Test Org",
                "description": "Test line description",
                "websites": ["https://test.example.com"],
                "meta": {
                    "created": "2025-01-10T00:00:00Z",
                    "changed": "2025-01-10T00:00:00Z",
                    "owner": {"uuid": "test-owner", "username": "testuser"},
                    "nid": 1,
                    "originating_system": "test"
                }
            }
        }
        
        self.test_traps = {
            "test-line-1": [
                {
                    "uuid": "test-trap-1",
                    "name": "Test Trap 1",
                    "project": self.test_lines["test-line-1"]["project"],
                    "line": self.test_lines["test-line-1"],
                    "tags": [{"tid": 3, "name": "trap-test", "uuid": "test-tag-3"}],
                    "is_listed": True,
                    "share_summary_data": True,
                    "curated": False,
                    "organisations": [{"name": "Test Org", "uuid": "test-org-1"}],
                    "contact": "test@example.com",
                    "contact_organisation": "Test Org",
                    "description": "Test trap description",
                    "websites": ["https://test.example.com"],
                    "trap_type": "DOC200",
                    "coordinates": {"coordinates": [174.0, -41.0], "bbox": [173.9, -41.1, 174.1, -40.9]},
                    "elevation": 100.0,
                    "last_check": "2025-01-10T12:00:00Z",
                    "last_reset": "2025-01-10T10:00:00Z",
                    "run_time": 7200,
                    "battery_voltage": 12.5,
                    "bar_state": "Set",
                    "eye_1": 1,
                    "eye_2": 1,
                    "ambient_1": 20,
                    "ambient_2": 20,
                    "life_cycles": 50,
                    "all_cycles": 100,
                    "cycles_by_eye": 25,
                    "bait_cycles": 10,
                    "possums": 5,
                    "days_between_baiting": 30,
                    "bait_run_time_seconds": 3600,
                    "set_state": True,
                    "runon": 1,
                    "prefeed_days": 3,
                    "temp_celsius": 18.5,
                    "hard_reboots": 0,
                    "last_error": "None",
                    "last_error_level": "Success",
                    "last_reboot_reason": "None",
                    "event": "Heartbeat",
                    "rcoms_reason": "NORMAL",
                    "long_log": "Test log entry",
                    "short_log": "Test",
                    "diary": "Test diary entry",
                    "eeprom": "Test eeprom data",
                    "rtcbu": "Test rtcbu data",
                    "extended": {"test_key": "test_value"},
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
                        "owner": {"uuid": "test-owner", "username": "testuser"},
                        "nid": 1,
                        "originating_system": "test"
                    }
                }
            ]
        }
        
        self.test_records = {
            "test-trap-1": [
                {
                    "uuid": "test-record-1",
                    "trap": self.test_traps["test-line-1"][0],
                    "project": self.test_lines["test-line-1"]["project"],
                    "line": self.test_lines["test-line-1"],
                    "date": "2025-01-10T12:00:00Z",
                    "event": "Heartbeat",
                    "status": "Set",
                    "rssi": -45.0,
                    "battery_voltage": 12.5,
                    "snr": 15.0,
                    "sensor_id": "test-sensor-1",
                    "sensor_provider": "test-provider",
                    "meta": {
                        "created": "2025-01-10T12:00:00Z",
                        "changed": "2025-01-10T12:00:00Z",
                        "owner": {"uuid": "test-owner", "username": "testuser"},
                        "nid": 1,
                        "originating_system": "test"
                    }
                }
            ]
        }
    
    async def get_line(self, line_uuid: str) -> Optional[Dict[str, Any]]:
        """Get a line by UUID"""
        if self.test_mode:
            if line_uuid in self.test_lines:
                return self.test_lines[line_uuid]
            return None
        
        # Real API call would go here
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{self.api_base_url}/lines/{line_uuid}")
                if response.status_code == 200:
                    return response.json()
                return None
            except Exception as e:
                logger.error(f"Error fetching line {line_uuid}: {e}")
                return None
    
    async def get_traps_by_line(self, line_uuid: str) -> Optional[Dict[str, Any]]:
        """Get traps for a specific line"""
        if self.test_mode:
            if line_uuid in self.test_traps:
                return {"items": self.test_traps[line_uuid]}
            return {"items": []}
        
        # Real API call would go here
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{self.api_base_url}/traps", params={"line": line_uuid})
                if response.status_code == 200:
                    return response.json()
                return None
            except Exception as e:
                logger.error(f"Error fetching traps for line {line_uuid}: {e}")
                return None
    
    async def get_trap_records(self, trap_uuid: str, limit: int = 1, sort_order: str = "desc", sort_column: str = "date") -> Optional[Dict[str, Any]]:
        """Get trap records for a specific trap"""
        if self.test_mode:
            if trap_uuid in self.test_records:
                return {"items": self.test_records[trap_uuid][:limit]}
            return {"items": []}
        
        # Real API call would go here
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.api_base_url}/traps/{trap_uuid}/records",
                    params={"limit": limit, "sort_order": sort_order, "sort_column": sort_column}
                )
                if response.status_code == 200:
                    return response.json()
                return None
            except Exception as e:
                logger.error(f"Error fetching records for trap {trap_uuid}: {e}")
                return None
    
    def add_test_line(self, line_uuid: str, line_data: Dict[str, Any]):
        """Add custom test line data"""
        if self.test_mode:
            self.test_lines[line_uuid] = line_data
            logger.info(f"Added test line: {line_uuid}")
        else:
            logger.warning("add_test_line only works in TEST_MODE")
    
    def add_test_trap(self, line_uuid: str, trap_data: Dict[str, Any]):
        """Add custom test trap data"""
        if self.test_mode:
            if line_uuid not in self.test_traps:
                self.test_traps[line_uuid] = []
            self.test_traps[line_uuid].append(trap_data)
            logger.info(f"Added test trap to line {line_uuid}: {trap_data.get('uuid', 'unknown')}")
        else:
            logger.warning("add_test_trap only works in TEST_MODE")
    
    def add_test_record(self, trap_uuid: str, record_data: Dict[str, Any]):
        """Add custom test trap record data"""
        if self.test_mode:
            if trap_uuid not in self.test_records:
                self.test_records[trap_uuid] = []
            self.test_records[trap_uuid].append(record_data)
            logger.info(f"Added test record to trap {trap_uuid}: {record_data.get('uuid', 'unknown')}")
        else:
            logger.warning("add_test_record only works in TEST_MODE")
    
    def clear_test_data(self):
        """Clear all test data"""
        if self.test_mode:
            self.test_lines.clear()
            self.test_traps.clear()
            self.test_records.clear()
            logger.info("Cleared all test data")
        else:
            logger.warning("clear_test_data only works in TEST_MODE")

class TrapNZDatabase:
    def __init__(self, db_path: str = "trapnz.db", api_base_url: str = "https://api2.trap.nz"):
        self.db_path = db_path
        self._api_facade = TrapNZAPIFacade(api_base_url)
        self.init_database()
        self.last_api_call = {}  # Track last API call time for each endpoint
    
    @property
    def api_facade(self) -> TrapNZAPIFacade:
        """Access to the API facade for test mode operations"""
        return self._api_facade
    
    def init_database(self):
        """Initialize the SQLite database with required tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create tables
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS projects (
                    uuid TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    location TEXT,
                    is_listed BOOLEAN,
                    share_summary_data BOOLEAN,
                    curated BOOLEAN,
                    contact TEXT,
                    contact_organisation TEXT,
                    description TEXT,
                    websites TEXT,
                    created TEXT,
                    changed TEXT,
                    owner_username TEXT,
                    nid INTEGER,
                    originating_system TEXT
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS organisations (
                    uuid TEXT PRIMARY KEY,
                    name TEXT NOT NULL
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tags (
                    uuid TEXT PRIMARY KEY,
                    tid INTEGER,
                    name TEXT NOT NULL
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS lines (
                    uuid TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    project_uuid TEXT,
                    is_listed BOOLEAN,
                    share_summary_data BOOLEAN,
                    curated BOOLEAN,
                    contact TEXT,
                    contact_organisation TEXT,
                    description TEXT,
                    websites TEXT,
                    created TEXT,
                    changed TEXT,
                    owner_username TEXT,
                    nid INTEGER,
                    originating_system TEXT,
                    FOREIGN KEY (project_uuid) REFERENCES projects (uuid)
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS traps (
                    uuid TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    project_uuid TEXT,
                    line_uuid TEXT,
                    trap_type TEXT,
                    elevation REAL,
                    last_check TEXT,
                    last_reset TEXT,
                    run_time INTEGER,
                    battery_voltage REAL,
                    bar_state TEXT,
                    eye_1 INTEGER,
                    eye_2 INTEGER,
                    ambient_1 INTEGER,
                    ambient_2 INTEGER,
                    life_cycles INTEGER,
                    all_cycles INTEGER,
                    cycles_by_eye INTEGER,
                    bait_cycles INTEGER,
                    possums INTEGER,
                    days_between_baiting INTEGER,
                    bait_run_time_seconds INTEGER,
                    set_state BOOLEAN,
                    runon INTEGER,
                    prefeed_days INTEGER,
                    temp_celsius REAL,
                    hard_reboots INTEGER,
                    last_error TEXT,
                    last_error_level TEXT,
                    last_reboot_reason TEXT,
                    event TEXT,
                    rcoms_reason TEXT,
                    long_log TEXT,
                    short_log TEXT,
                    diary TEXT,
                    eeprom TEXT,
                    rtcbu TEXT,
                    extended TEXT,
                    set_status TEXT,
                    battery_health TEXT,
                    eye_1_health TEXT,
                    eye_2_health TEXT,
                    reboot_reason_health TEXT,
                    overall_health TEXT,
                    trap_status_reasons TEXT,
                    coordinates_lon REAL,
                    coordinates_lat REAL,
                    created TEXT,
                    changed TEXT,
                    owner_username TEXT,
                    nid INTEGER,
                    originating_system TEXT,
                    FOREIGN KEY (project_uuid) REFERENCES projects (uuid),
                    FOREIGN KEY (line_uuid) REFERENCES lines (uuid)
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS trap_records (
                    uuid TEXT PRIMARY KEY,
                    trap_uuid TEXT,
                    project_uuid TEXT,
                    line_uuid TEXT,
                    date TEXT,
                    event TEXT,
                    status TEXT,
                    rssi REAL,
                    battery_voltage REAL,
                    snr REAL,
                    sensor_id TEXT,
                    sensor_provider TEXT,
                    created TEXT,
                    changed TEXT,
                    owner_username TEXT,
                    nid INTEGER,
                    originating_system TEXT,
                    FOREIGN KEY (trap_uuid) REFERENCES traps (uuid),
                    FOREIGN KEY (project_uuid) REFERENCES projects (uuid),
                    FOREIGN KEY (line_uuid) REFERENCES lines (uuid)
                )
            """)
            
            # Junction tables for many-to-many relationships
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS project_organisations (
                    project_uuid TEXT,
                    organisation_uuid TEXT,
                    PRIMARY KEY (project_uuid, organisation_uuid),
                    FOREIGN KEY (project_uuid) REFERENCES projects (uuid),
                    FOREIGN KEY (organisation_uuid) REFERENCES organisations (uuid)
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS project_tags (
                    project_uuid TEXT,
                    tag_uuid TEXT,
                    PRIMARY KEY (project_uuid, tag_uuid),
                    FOREIGN KEY (project_uuid) REFERENCES projects (uuid),
                    FOREIGN KEY (tag_uuid) REFERENCES tags (uuid)
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS line_organisations (
                    line_uuid TEXT,
                    organisation_uuid TEXT,
                    PRIMARY KEY (line_uuid, organisation_uuid),
                    FOREIGN KEY (line_uuid) REFERENCES lines (uuid),
                    FOREIGN KEY (organisation_uuid) REFERENCES organisations (uuid)
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS line_tags (
                    line_uuid TEXT,
                    tag_uuid TEXT,
                    PRIMARY KEY (line_uuid, tag_uuid),
                    FOREIGN KEY (line_uuid) REFERENCES lines (uuid),
                    FOREIGN KEY (tag_uuid) REFERENCES tags (uuid)
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS trap_organisations (
                    trap_uuid TEXT,
                    organisation_uuid TEXT,
                    PRIMARY KEY (trap_uuid, organisation_uuid),
                    FOREIGN KEY (trap_uuid) REFERENCES traps (uuid),
                    FOREIGN KEY (organisation_uuid) REFERENCES organisations (uuid)
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS trap_tags (
                    trap_uuid TEXT,
                    tag_uuid TEXT,
                    PRIMARY KEY (trap_uuid, tag_uuid),
                    FOREIGN KEY (trap_uuid) REFERENCES traps (uuid),
                    FOREIGN KEY (tag_uuid) REFERENCES tags (uuid)
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS volunteer (
                    name TEXT,
                    preferences TEXT,
                    PRIMARY KEY (name)
                )
            """)
            
            conn.commit()
    
    def _store_meta(self, cursor: sqlite3.Cursor, meta: Meta, table_name: str, record_uuid: str):
        """Store metadata in the specified table"""
        cursor.execute(f"""
            UPDATE {table_name} SET
                created = ?, changed = ?, owner_username = ?, nid = ?, originating_system = ?
            WHERE uuid = ?
        """, (
            meta.created.isoformat(),
            meta.changed.isoformat(),
            meta.owner.get('username', ''),
            meta.nid,
            meta.originating_system,
            record_uuid
        ))
    
    def _store_coordinates(self, cursor: sqlite3.Cursor, coordinates: Coordinates, trap_uuid: str):
        """Store coordinates for a trap"""
        if coordinates.coordinates and len(coordinates.coordinates) >= 2:
            cursor.execute("""
                UPDATE traps SET coordinates_lon = ?, coordinates_lat = ? WHERE uuid = ?
            """, (coordinates.coordinates[0], coordinates.coordinates[1], trap_uuid))
    
    def store_project(self, project: Project):
        """Store a project in the database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Store project
            cursor.execute("""
                INSERT OR REPLACE INTO projects (
                    uuid, name, location, is_listed, share_summary_data, curated,
                    contact, contact_organisation, description, websites
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                str(project.uuid), project.name, project.location,
                project.is_listed, project.share_summary_data, project.curated,
                project.contact, project.contact_organisation,
                project.description, json.dumps(project.websites)
            ))
            
            # Store metadata
            self._store_meta(cursor, project.meta, 'projects', str(project.uuid))
            
            # Store organisations
            for org in project.organisations:
                cursor.execute("""
                    INSERT OR REPLACE INTO organisations (uuid, name) VALUES (?, ?)
                """, (str(org.uuid), org.name))
                
                cursor.execute("""
                    INSERT OR REPLACE INTO project_organisations (project_uuid, organisation_uuid)
                    VALUES (?, ?)
                """, (str(project.uuid), str(org.uuid)))
            
            # Store tags
            for tag in project.tags:
                cursor.execute("""
                    INSERT OR REPLACE INTO tags (uuid, tid, name) VALUES (?, ?, ?)
                """, (str(tag.uuid), tag.tid, tag.name))
                
                cursor.execute("""
                    INSERT OR REPLACE INTO project_tags (project_uuid, tag_uuid)
                    VALUES (?, ?)
                """, (str(project.uuid), str(tag.uuid)))
            
            conn.commit()
    
    def store_line(self, line: Line):
        """Store a line in the database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Store line
            cursor.execute("""
                INSERT OR REPLACE INTO lines (
                    uuid, name, project_uuid, is_listed, share_summary_data, curated,
                    contact, contact_organisation, description, websites
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                str(line.uuid), line.name, str(line.project.uuid),
                line.is_listed, line.share_summary_data, line.curated,
                line.contact, line.contact_organisation,
                line.description, json.dumps(line.websites)
            ))
            
            # Store metadata
            self._store_meta(cursor, line.meta, 'lines', str(line.uuid))
            
            # Store organisations
            for org in line.organisations:
                cursor.execute("""
                    INSERT OR REPLACE INTO organisations (uuid, name) VALUES (?, ?)
                """, (str(org.uuid), org.name))
                
                cursor.execute("""
                    INSERT OR REPLACE INTO line_organisations (line_uuid, organisation_uuid)
                    VALUES (?, ?)
                """, (str(line.uuid), str(org.uuid)))
            
            # Store tags
            for tag in line.tags:
                cursor.execute("""
                    INSERT OR REPLACE INTO tags (uuid, tid, name) VALUES (?, ?, ?)
                """, (str(tag.uuid), tag.tid, tag.name))
                
                cursor.execute("""
                    INSERT OR REPLACE INTO line_tags (line_uuid, tag_uuid)
                    VALUES (?, ?)
                """, (str(line.uuid), str(tag.uuid)))
            
            conn.commit()
    
    def store_trap(self, trap: Trap):
        """Store a trap in the database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Store trap
            cursor.execute("""
                INSERT OR REPLACE INTO traps (
                    uuid, name, project_uuid, line_uuid, trap_type, elevation,
                    last_check, last_reset, run_time, battery_voltage, bar_state,
                    eye_1, eye_2, ambient_1, ambient_2, life_cycles, all_cycles,
                    cycles_by_eye, bait_cycles, possums, days_between_baiting,
                    bait_run_time_seconds, set_state, runon, prefeed_days,
                    temp_celsius, hard_reboots, last_error, last_error_level,
                    last_reboot_reason, event, rcoms_reason, long_log, short_log,
                    diary, eeprom, rtcbu, extended, set_status, battery_health,
                    eye_1_health, eye_2_health, reboot_reason_health, overall_health,
                    trap_status_reasons
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                str(trap.uuid), trap.name, str(trap.project.uuid), str(trap.line.uuid),
                trap.trap_type, trap.elevation, trap.last_check.isoformat() if trap.last_check else None,
                trap.last_reset.isoformat() if trap.last_reset else None, trap.run_time,
                trap.battery_voltage, trap.bar_state, trap.eye_1, trap.eye_2,
                trap.ambient_1, trap.ambient_2, trap.life_cycles, trap.all_cycles,
                trap.cycles_by_eye, trap.bait_cycles, trap.possums, trap.days_between_baiting,
                trap.bait_run_time_seconds, trap.set_state, trap.runon, trap.prefeed_days,
                trap.temp_celsius, trap.hard_reboots, trap.last_error, trap.last_error_level,
                trap.last_reboot_reason, trap.event, trap.rcoms_reason, trap.long_log,
                trap.short_log, trap.diary, trap.eeprom, trap.rtcbu, json.dumps(trap.extended),
                trap.set_status, trap.battery_health, trap.eye_1_health, trap.eye_2_health,
                trap.reboot_reason_health, trap.overall_health, json.dumps(trap.trap_status_reasons)
            ))
            
            # Store metadata
            self._store_meta(cursor, trap.meta, 'traps', str(trap.uuid))
            
            # Store coordinates
            self._store_coordinates(cursor, trap.coordinates, str(trap.uuid))
            
            # Store organisations
            for org in trap.organisations:
                cursor.execute("""
                    INSERT OR REPLACE INTO organisations (uuid, name) VALUES (?, ?)
                """, (str(org.uuid), org.name))
                
                cursor.execute("""
                    INSERT OR REPLACE INTO trap_organisations (trap_uuid, organisation_uuid)
                    VALUES (?, ?)
                """, (str(trap.uuid), str(org.uuid)))
            
            # Store tags
            for tag in trap.tags:
                cursor.execute("""
                    INSERT OR REPLACE INTO tags (uuid, tid, name) VALUES (?, ?, ?)
                """, (str(tag.uuid), tag.tid, tag.name))
                
                cursor.execute("""
                    INSERT OR REPLACE INTO trap_tags (trap_uuid, tag_uuid)
                    VALUES (?, ?)
                """, (str(trap.uuid), str(tag.uuid)))
            
            conn.commit()
    
    def store_trap_record(self, record: TrapRecord):
        """Store a trap record in the database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO trap_records (
                    uuid, trap_uuid, project_uuid, line_uuid, date, event, status,
                    rssi, battery_voltage, snr, sensor_id, sensor_provider
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                str(record.uuid), str(record.trap.uuid), str(record.project.uuid),
                str(record.line.uuid), record.date.isoformat(), record.event, record.status,
                record.rssi, record.battery_voltage, record.snr, record.sensor_id, record.sensor_provider
            ))
            
            # Store metadata
            self._store_meta(cursor, record.meta, 'trap_records', str(record.uuid))
            
            conn.commit()
    
    def _needs_refresh(self, endpoint: str, force_refresh: bool = False) -> bool:
        """
        Check if data needs to be refreshed from API
        
        Args:
            endpoint: API endpoint name (e.g., 'lines', 'traps', 'records')
            force_refresh: If True, always return True
            
        Returns:
            True if data needs refresh, False otherwise
        """
        if force_refresh:
            return True
        
        if endpoint not in self.last_api_call:
            return True
        
        from datetime import datetime, timedelta
        time_since_last_call = datetime.now() - self.last_api_call[endpoint]
        return time_since_last_call > timedelta(hours=1)
    
    def _update_api_call_time(self, endpoint: str):
        """Update the last API call time for an endpoint"""
        from datetime import datetime
        self.last_api_call[endpoint] = datetime.now()
    
    async def fetch_lines_by_uuids(self, line_uuids: List[UUID], force_refresh: bool = False) -> List[Line]:
        """Fetch lines from the API by their UUIDs"""
        # Check if we need to refresh from API
        if not self._needs_refresh('lines', force_refresh):
            logger.info("Using cached lines data (less than 1 hour old)")
            return self.get_lines_by_uuids(line_uuids)
        
        logger.info("Fetching lines from API (cache expired or force refresh)")
        lines = []
        
        for line_uuid in line_uuids:
            try:
                line_data = await self.api_facade.get_line(str(line_uuid))
                if line_data:
                    line = Line(**line_data)
                    lines.append(line)
                    # Store in database
                    self.store_line(line)
                else:
                    logger.warning(f"No data returned for line {line_uuid}")
            except Exception as e:
                logger.error(f"Error fetching line {line_uuid}: {e}")
        
        # Update API call time
        self._update_api_call_time('lines')
        return lines
    
    def get_lines_by_uuids(self, line_uuids: List[UUID]) -> List[Line]:
        """Retrieve lines from local database by UUIDs"""
        lines = []
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            for line_uuid in line_uuids:
                try:
                    # Get line data
                    cursor.execute("""
                        SELECT uuid, name, project_uuid, is_listed, share_summary_data, curated,
                               contact, contact_organisation, description, websites,
                               created, changed, owner_username, nid, originating_system
                        FROM lines WHERE uuid = ?
                    """, (str(line_uuid),))
                    
                    line_row = cursor.fetchone()
                    if line_row:
                        # Get project data
                        cursor.execute("""
                            SELECT uuid, name, location, is_listed, share_summary_data, curated,
                                   contact, contact_organisation, description, websites,
                                   created, changed, owner_username, nid, originating_system
                            FROM projects WHERE uuid = ?
                        """, (line_row[2],))  # project_uuid
                        
                        project_row = cursor.fetchone()
                        if project_row:
                            # Get project organisations
                            cursor.execute("""
                                SELECT o.uuid, o.name FROM organisations o
                                JOIN project_organisations po ON o.uuid = po.organisation_uuid
                                WHERE po.project_uuid = ?
                            """, (project_row[0],))
                            
                            project_orgs = [{"uuid": row[0], "name": row[1]} for row in cursor.fetchall()]
                            
                            # Get project tags
                            cursor.execute("""
                                SELECT t.uuid, t.tid, t.name FROM tags t
                                JOIN project_tags pt ON t.uuid = pt.tag_uuid
                                WHERE pt.project_uuid = ?
                            """, (project_row[0],))
                            
                            project_tags = [{"uuid": row[0], "tid": row[1], "name": row[2]} for row in cursor.fetchall()]
                            
                            # Get line organisations
                            cursor.execute("""
                                SELECT o.uuid, o.name FROM organisations o
                                JOIN line_organisations lo ON o.uuid = lo.organisation_uuid
                                WHERE lo.line_uuid = ?
                            """, (line_row[0],))
                            
                            line_orgs = [{"uuid": row[0], "name": row[1]} for row in cursor.fetchall()]
                            
                            # Get line tags
                            cursor.execute("""
                                SELECT t.uuid, t.tid, t.name FROM tags t
                                JOIN line_tags lt ON t.uuid = lt.tag_uuid
                                WHERE lt.line_uuid = ?
                            """, (line_row[0],))
                            
                            line_tags = [{"uuid": row[0], "tid": row[1], "name": row[2]} for row in cursor.fetchall()]
                            
                            # Create Line object
                            line = Line(
                                uuid=UUID(line_row[0]),
                                name=line_row[1],
                                project=Project(
                                    uuid=UUID(project_row[0]),
                                    name=project_row[1],
                                    location=project_row[2],
                                    tags=[Tag(**tag) for tag in project_tags],
                                    is_listed=bool(project_row[3]),
                                    share_summary_data=bool(project_row[4]),
                                    curated=bool(project_row[5]),
                                    organisations=[Organisation(**org) for org in project_orgs],
                                    contact=project_row[6],
                                    contact_organisation=project_row[7],
                                    description=project_row[8],
                                    websites=json.loads(project_row[9]) if project_row[9] else [],
                                    meta=Meta(
                                        created=datetime.fromisoformat(project_row[10]),
                                        changed=datetime.fromisoformat(project_row[11]),
                                        owner={"username": project_row[12]},
                                        nid=project_row[13],
                                        originating_system=project_row[14]
                                    )
                                ),
                                tags=[Tag(**tag) for tag in line_tags],
                                is_listed=bool(line_row[3]),
                                share_summary_data=bool(line_row[4]),
                                curated=bool(line_row[5]),
                                organisations=[Organisation(**org) for org in line_orgs],
                                contact=line_row[6],
                                contact_organisation=line_row[7],
                                description=line_row[8],
                                websites=json.loads(line_row[9]) if line_row[9] else [],
                                meta=Meta(
                                    created=datetime.fromisoformat(line_row[10]),
                                    changed=datetime.fromisoformat(line_row[11]),
                                    owner={"username": line_row[12]},
                                    nid=line_row[13],
                                    originating_system=line_row[14]
                                )
                            )
                            lines.append(line)
                            
                except Exception as e:
                    logger.error(f"Error retrieving line {line_uuid} from database: {e}")
        
        return lines
    
    async def fetch_traps_by_line_uuids(self, line_uuids: List[UUID], force_refresh: bool = False) -> List[Trap]:
        """Fetch all traps in the specified lines"""
        # Check if we need to refresh from API
        if not self._needs_refresh('traps', force_refresh):
            logger.info("Using cached traps data (less than 1 hour old)")
            return self.get_traps_by_line_uuids(line_uuids)
        
        logger.info("Fetching traps from API (cache expired or force refresh)")
        traps = []
        
        for line_uuid in line_uuids:
            try:
                trap_data = await self.api_facade.get_traps_by_line(str(line_uuid))
                if trap_data and trap_data.get("items"):
                    for trap_item in trap_data.get("items", []):
                        trap = Trap(**trap_item)
                        traps.append(trap)
                        # Store in database
                        self.store_trap(trap)
                else:
                    logger.info(f"No traps found for line {line_uuid}")
            except Exception as e:
                logger.error(f"Error fetching traps for line {line_uuid}: {e}")
        
        # Update API call time
        self._update_api_call_time('traps')
        return traps
    
    def get_traps_by_line_uuids(self, line_uuids: List[UUID]) -> List[Trap]:
        """Retrieve traps from local database by line UUIDs"""
        traps = []
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            for line_uuid in line_uuids:
                try:
                    cursor.execute("""
                        SELECT uuid, name, project_uuid, line_uuid, trap_type, elevation,
                               last_check, last_reset, run_time, battery_voltage, bar_state,
                               eye_1, eye_2, ambient_1, ambient_2, life_cycles, all_cycles,
                               cycles_by_eye, bait_cycles, possums, days_between_baiting,
                               bait_run_time_seconds, set_state, runon, prefeed_days,
                               temp_celsius, hard_reboots, last_error, last_error_level,
                               last_reboot_reason, event, rcoms_reason, long_log, short_log,
                               diary, eeprom, rtcbu, extended, set_status, battery_health,
                               eye_1_health, eye_2_health, reboot_reason_health, overall_health,
                               trap_status_reasons, coordinates_lon, coordinates_lat,
                               created, changed, owner_username, nid, originating_system
                        FROM traps WHERE line_uuid = ?
                    """, (str(line_uuid),))
                    
                    trap_rows = cursor.fetchall()
                    for trap_row in trap_rows:
                        # Get project and line data (simplified for brevity)
                        # In a full implementation, you'd reconstruct the full objects
                        trap = Trap(
                            uuid=UUID(trap_row[0]),
                            name=trap_row[1],
                            project=Project(uuid=UUID(trap_row[2]), name="", location="", tags=[], 
                                         is_listed=True, share_summary_data=True, curated=False,
                                         organisations=[], contact="", contact_organisation="",
                                         description="", websites=[], meta=Meta(
                                             created=datetime.now(), changed=datetime.now(),
                                             owner={"username": ""}, nid=0, originating_system=""
                                         )),
                            line=Line(uuid=UUID(trap_row[3]), name="", project=Project(uuid=UUID(trap_row[2]), name="", location="", tags=[], 
                                         is_listed=True, share_summary_data=True, curated=False,
                                         organisations=[], contact="", contact_organisation="",
                                         description="", websites=[], meta=Meta(
                                             created=datetime.now(), changed=datetime.now(),
                                             owner={"username": ""}, nid=0, originating_system=""
                                         )), tags=[], is_listed=True, share_summary_data=True, curated=False,
                                         organisations=[], contact="", contact_organisation="",
                                         description="", websites=[], meta=Meta(
                                             created=datetime.now(), changed=datetime.now(),
                                             owner={"username": ""}, nid=0, originating_system=""
                                         )),
                            tags=[],
                            is_listed=True,
                            share_summary_data=True,
                            curated=False,
                            organisations=[],
                            contact="",
                            contact_organisation="",
                            description="",
                            websites=[],
                            trap_type=trap_row[4],
                            elevation=trap_row[5] or 0.0,
                            last_check=datetime.fromisoformat(trap_row[6]) if trap_row[6] else None,
                            last_reset=datetime.fromisoformat(trap_row[7]) if trap_row[7] else None,
                            run_time=trap_row[8] or 0,
                            battery_voltage=trap_row[9] or 0.0,
                            bar_state=trap_row[10] or "",
                            eye_1=trap_row[11] or 0,
                            eye_2=trap_row[12] or 0,
                            ambient_1=trap_row[13] or 0,
                            ambient_2=trap_row[14] or 0,
                            life_cycles=trap_row[15] or 0,
                            all_cycles=trap_row[16] or 0,
                            cycles_by_eye=trap_row[17] or 0,
                            bait_cycles=trap_row[18] or 0,
                            possums=trap_row[19] or 0,
                            days_between_baiting=trap_row[20] or 0,
                            bait_run_time_seconds=trap_row[21] or 0,
                            set_state=bool(trap_row[22]),
                            runon=trap_row[23] or 0,
                            prefeed_days=trap_row[24] or 0,
                            temp_celsius=trap_row[25] or 0.0,
                            hard_reboots=trap_row[26] or 0,
                            last_error=trap_row[27] or "",
                            last_error_level=trap_row[28] or "",
                            last_reboot_reason=trap_row[29] or "",
                            event=trap_row[30] or "",
                            rcoms_reason=trap_row[31] or "",
                            long_log=trap_row[32] or "",
                            short_log=trap_row[33] or "",
                            diary=trap_row[34] or "",
                            eeprom=trap_row[35] or "",
                            rtcbu=trap_row[36] or "",
                            extended=json.loads(trap_row[37]) if trap_row[37] else {},
                            set_status=trap_row[38] or "",
                            battery_health=trap_row[39] or "",
                            eye_1_health=trap_row[40] or "",
                            eye_2_health=trap_row[41] or "",
                            reboot_reason_health=trap_row[42] or "",
                            overall_health=trap_row[43] or "",
                            trap_status_reasons=json.loads(trap_row[44]) if trap_row[44] else [],
                            coordinates=Coordinates(
                                coordinates=[trap_row[45] or 0.0, trap_row[46] or 0.0],
                                bbox=[0.0, 0.0, 0.0, 0.0]
                            ),
                            meta=Meta(
                                created=datetime.fromisoformat(trap_row[47]),
                                changed=datetime.fromisoformat(trap_row[48]),
                                owner={"username": trap_row[49]},
                                nid=trap_row[50],
                                originating_system=trap_row[51]
                            )
                        )
                        traps.append(trap)
                        
                except Exception as e:
                    logger.error(f"Error retrieving traps for line {line_uuid} from database: {e}")
        
        return traps
    
    async def fetch_latest_records_for_traps(self, trap_uuids: List[UUID], force_refresh: bool = False) -> List[TrapRecord]:
        """Fetch the latest record for each trap"""
        # Check if we need to refresh from API
        if not self._needs_refresh('records', force_refresh):
            logger.info("Using cached trap records data (less than 1 hour old)")
            return self.get_latest_records_for_traps(trap_uuids)
        
        logger.info("Fetching trap records from API (cache expired or force refresh)")
        records = []
        
        for trap_uuid in trap_uuids:
            try:
                # Get latest record for this trap
                record_data = await self.api_facade.get_trap_records(
                    str(trap_uuid), 
                    limit=1, 
                    sort_order="desc", 
                    sort_column="date"
                )
                if record_data and record_data.get("items"):
                    record = TrapRecord(**record_data["items"][0])
                    records.append(record)
                    # Store in database
                    self.store_trap_record(record)
                else:
                    logger.info(f"No records found for trap {trap_uuid}")
            except Exception as e:
                logger.error(f"Error fetching latest record for trap {trap_uuid}: {e}")
        
        # Update API call time
        self._update_api_call_time('records')
        return records
    
    def get_latest_records_for_traps(self, trap_uuids: List[UUID]) -> List[TrapRecord]:
        """Retrieve latest trap records from local database by trap UUIDs"""
        records = []
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            for trap_uuid in trap_uuids:
                try:
                    # Get the latest record for this trap
                    cursor.execute("""
                        SELECT uuid, trap_uuid, project_uuid, line_uuid, date, event, status,
                               rssi, battery_voltage, snr, sensor_id, sensor_provider,
                               created, changed, owner_username, nid, originating_system
                        FROM trap_records 
                        WHERE trap_uuid = ? 
                        ORDER BY date DESC 
                        LIMIT 1
                    """, (str(trap_uuid),))
                    
                    record_row = cursor.fetchone()
                    if record_row:
                        # Create simplified objects for the record
                        # Note: This is a simplified version - full objects would need complete reconstruction
                        dummy_project = Project(
                            uuid=UUID(record_row[2]), name="", location="", tags=[], 
                            is_listed=True, share_summary_data=True, curated=False,
                            organisations=[], contact="", contact_organisation="",
                            description="", websites=[], 
                            meta=Meta(created=datetime.now(), changed=datetime.now(),
                                    owner={"username": ""}, nid=0, originating_system="")
                        )
                        
                        dummy_line = Line(
                            uuid=UUID(record_row[3]), name="", project=dummy_project, tags=[], 
                            is_listed=True, share_summary_data=True, curated=False,
                            organisations=[], contact="", contact_organisation="",
                            description="", websites=[], 
                            meta=Meta(created=datetime.now(), changed=datetime.now(),
                                    owner={"username": ""}, nid=0, originating_system="")
                        )
                        
                        dummy_trap = Trap(
                            uuid=UUID(record_row[1]), name="", project=dummy_project, line=dummy_line, tags=[], 
                            is_listed=True, share_summary_data=True, curated=False,
                            organisations=[], contact="", contact_organisation="",
                            description="", websites=[], trap_type="", 
                            coordinates=Coordinates(coordinates=[0.0, 0.0], bbox=[0.0, 0.0, 0.0, 0.0]), 
                            elevation=0.0, last_check=None, last_reset=None, run_time=0, battery_voltage=0.0, 
                            bar_state="", eye_1=0, eye_2=0, ambient_1=0, ambient_2=0, life_cycles=0, 
                            all_cycles=0, cycles_by_eye=0, bait_cycles=0, possums=0, days_between_baiting=0, 
                            bait_run_time_seconds=0, set_state=False, runon=0, prefeed_days=0, temp_celsius=0.0, 
                            hard_reboots=0, last_error="", last_error_level="", last_reboot_reason="", event="", 
                            rcoms_reason="", long_log="", short_log="", diary="", eeprom="", rtcbu="", 
                            extended={}, set_status="", battery_health="", eye_1_health="", eye_2_health="", 
                            reboot_reason_health="", overall_health="", trap_status_reasons=[],
                            meta=Meta(created=datetime.now(), changed=datetime.now(),
                                    owner={"username": ""}, nid=0, originating_system="")
                        )
                        
                        record = TrapRecord(
                            uuid=UUID(record_row[0]),
                            trap=dummy_trap,
                            project=dummy_project,
                            line=dummy_line,
                            date=datetime.fromisoformat(record_row[4]),
                            event=record_row[5],
                            status=record_row[6],
                            rssi=record_row[7],
                            battery_voltage=record_row[8],
                            snr=record_row[9],
                            sensor_id=record_row[10],
                            sensor_provider=record_row[11],
                            meta=Meta(
                                created=datetime.fromisoformat(record_row[12]),
                                changed=datetime.fromisoformat(record_row[13]),
                                owner={"username": record_row[14]},
                                nid=record_row[15],
                                originating_system=record_row[16]
                            )
                        )
                        records.append(record)
                        
                except Exception as e:
                    logger.error(f"Error retrieving record for trap {trap_uuid} from database: {e}")
        
        return records
    
    async def retrieve_lines_traps_and_records(self, line_uuids: List[UUID], force_refresh: bool = False) -> Dict[str, Any]:
        """Main method to retrieve lines, traps, and latest records"""
        logger.info(f"Fetching {len(line_uuids)} lines...")
        lines = await self.fetch_lines_by_uuids(line_uuids, force_refresh)
        logger.info(f"Retrieved {len(lines)} lines")
        
        logger.info(f"Fetching traps for {len(line_uuids)} lines...")
        traps = await self.fetch_traps_by_line_uuids(line_uuids, force_refresh)
        logger.info(f"Retrieved {len(traps)} traps")
        
        trap_uuids = [trap.uuid for trap in traps]
        logger.info(f"Fetching latest records for {len(trap_uuids)} traps...")
        records = await self.fetch_latest_records_for_traps(trap_uuids, force_refresh)
        logger.info(f"Retrieved {len(records)} records")
        
        return {
            "lines": lines,
            "traps": traps,
            "records": records
        }
    
    def get_all_lines(self) -> List[Line]:
        """Retrieve all lines from the local database"""
        lines = []
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT uuid FROM lines
            """)
            
            line_uuids = [UUID(row[0]) for row in cursor.fetchall()]
            lines = self.get_lines_by_uuids(line_uuids)
        
        return lines
    
    def get_all_traps(self) -> List[Trap]:
        """Retrieve all traps from the local database"""
        traps = []
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT DISTINCT line_uuid FROM traps
            """)
            
            line_uuids = [UUID(row[0]) for row in cursor.fetchall()]
            traps = self.get_traps_by_line_uuids(line_uuids)
        
        return traps
    
    def get_all_trap_records(self) -> List[TrapRecord]:
        """Retrieve all trap records from the local database"""
        records = []
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT DISTINCT trap_uuid FROM trap_records
            """)
            
            trap_uuids = [UUID(row[0]) for row in cursor.fetchall()]
            records = self.get_latest_records_for_traps(trap_uuids)
        
        return records
    
    def get_trap_records_by_trap(self, trap_uuid: UUID, limit: int = 100) -> List[TrapRecord]:
        """Retrieve multiple trap records for a specific trap"""
        records = []
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT uuid, trap_uuid, project_uuid, line_uuid, date, event, status,
                       rssi, battery_voltage, snr, sensor_id, sensor_provider,
                       created, changed, owner_username, nid, originating_system
                FROM trap_records 
                WHERE trap_uuid = ? 
                ORDER BY date DESC 
                LIMIT ?
            """, (str(trap_uuid), limit))
            
            record_rows = cursor.fetchall()
            for record_row in record_rows:
                try:
                    # Create simplified objects (similar to get_latest_records_for_traps)
                    dummy_project = Project(
                        uuid=UUID(record_row[2]), name="", location="", tags=[], 
                        is_listed=True, share_summary_data=True, curated=False,
                        organisations=[], contact="", contact_organisation="",
                        description="", websites=[], 
                        meta=Meta(created=datetime.now(), changed=datetime.now(),
                                owner={"username": ""}, nid=0, originating_system="")
                    )
                    
                    dummy_line = Line(
                        uuid=UUID(record_row[3]), name="", project=dummy_project, tags=[], 
                        is_listed=True, share_summary_data=True, curated=False,
                        organisations=[], contact="", contact_organisation="",
                        description="", websites=[], 
                        meta=Meta(created=datetime.now(), changed=datetime.now(),
                                owner={"username": ""}, nid=0, originating_system="")
                    )
                    
                    dummy_trap = Trap(
                        uuid=UUID(record_row[1]), name="", project=dummy_project, line=dummy_line, tags=[], 
                        is_listed=True, share_summary_data=True, curated=False,
                        organisations=[], contact="", contact_organisation="",
                        description="", websites=[], trap_type="", 
                        coordinates=Coordinates(coordinates=[0.0, 0.0], bbox=[0.0, 0.0, 0.0, 0.0]), 
                        elevation=0.0, last_check=None, last_reset=None, run_time=0, battery_voltage=0.0, 
                        bar_state="", eye_1=0, eye_2=0, ambient_1=0, ambient_2=0, life_cycles=0, 
                        all_cycles=0, cycles_by_eye=0, bait_cycles=0, possums=0, days_between_baiting=0, 
                        bait_run_time_seconds=0, set_state=False, runon=0, prefeed_days=0, temp_celsius=0.0, 
                        hard_reboots=0, last_error="", last_error_level="", last_reboot_reason="", event="", 
                        rcoms_reason="", long_log="", short_log="", diary="", eeprom="", rtcbu="", 
                        extended={}, set_status="", battery_health="", eye_1_health="", eye_2_health="", 
                        reboot_reason_health="", overall_health="", trap_status_reasons=[],
                        meta=Meta(created=datetime.now(), changed=datetime.now(),
                                owner={"username": ""}, nid=0, originating_system="")
                    )
                    
                    record = TrapRecord(
                        uuid=UUID(record_row[0]),
                        trap=dummy_trap,
                        project=dummy_project,
                        line=dummy_line,
                        date=datetime.fromisoformat(record_row[4]),
                        event=record_row[5],
                        status=record_row[6],
                        rssi=record_row[7],
                        battery_voltage=record_row[8],
                        snr=record_row[9],
                        sensor_id=record_row[10],
                        sensor_provider=record_row[11],
                        meta=Meta(
                            created=datetime.fromisoformat(record_row[12]),
                            changed=datetime.fromisoformat(record_row[13]),
                            owner={"username": record_row[14]},
                            nid=record_row[15],
                            originating_system=record_row[16]
                        )
                    )
                    records.append(record)
                    
                except Exception as e:
                    logger.error(f"Error creating trap record object: {e}")
        
        return records

    def get_volunteers(self) -> List[Volunteer]:
            """Retrieve all volunteers and their preferences"""
            records = []
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT *  FROM Volunteer
                """)
                
                trap_uuids = [UUID(row[0]) for row in cursor.fetchall()]
                records = self.get_latest_records_for_traps(trap_uuids)
            
            return records

    def store_volunteer(self, volunteer: Volunteer):
        """Store a volunteer in the database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Store project
            cursor.execute("""
                INSERT OR REPLACE INTO volunteer (
                    name, preferences
                ) VALUES (?, ?)
            """, (
                volunteer.name, volunteer.preferences
            ))
            
            # Store metadata
            self._store_meta(cursor, volunteer.meta, 'volunteers', volunteer.name)
            
            conn.commit()