"""
This module provides access to TrapNZ data and manages an active cache of 
trap status as well as volunteers and their preferences


"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from uuid import UUID

# Base models for common fields
class Meta(BaseModel):
    created: datetime
    changed: datetime
    owner: Dict[str, Any]  # Contains uuid and username
    nid: int
    originating_system: str

class Coordinates(BaseModel):
    coordinates: List[float] = Field(description="[longitude, latitude]")
    bbox: List[float] = Field(description="[min_lon, min_lat, max_lon, max_lat]")

class Tag(BaseModel):
    tid: int
    name: str
    uuid: UUID

class Organisation(BaseModel):
    name: str
    uuid: UUID

class Project(BaseModel):
    uuid: UUID
    name: str
    location: str
    tags: List[Tag]
    is_listed: bool
    share_summary_data: bool
    curated: bool
    organisations: List[Organisation]
    contact: str
    contact_organisation: str
    description: str
    websites: List[str]
    meta: Meta

# Line Models
class Line(BaseModel):
    uuid: UUID
    name: str
    project: Project
    tags: List[Tag]
    is_listed: bool
    share_summary_data: bool
    curated: bool
    organisations: List[Organisation]
    contact: str
    contact_organisation: str
    description: str
    websites: List[str]
    meta: Meta

# Trap Models
class Trap(BaseModel):
    uuid: UUID
    name: str
    project: Project
    line: Line
    tags: List[Tag]
    is_listed: bool
    share_summary_data: bool
    curated: bool
    organisations: List[Organisation]
    contact: str
    contact_organisation: str
    description: str
    websites: List[str]
    meta: Meta
    # Trap-specific fields
    trap_type: str
    coordinates: Coordinates
    elevation: float
    last_check: Optional[datetime] = None
    last_reset: Optional[datetime] = None
    run_time: int
    battery_voltage: float
    bar_state: str
    eye_1: int
    eye_2: int
    ambient_1: int
    ambient_2: int
    life_cycles: int
    all_cycles: int
    cycles_by_eye: int
    bait_cycles: int
    possums: int
    days_between_baiting: int
    bait_run_time_seconds: int
    set_state: bool
    runon: int
    prefeed_days: int
    temp_celsius: float
    hard_reboots: int
    last_error: str
    last_error_level: str
    last_reboot_reason: str
    event: str
    rcoms_reason: str
    long_log: str
    short_log: str
    diary: str
    eeprom: str
    rtcbu: str
    extended: Dict[str, Any]
    set_status: str
    battery_health: str
    eye_1_health: str
    eye_2_health: str
    reboot_reason_health: str
    overall_health: str
    trap_status_reasons: List[str]



# Trap Record Models
class TrapRecord(BaseModel):
    uuid: UUID
    trap: Trap
    project: Project
    line: Line
    meta: Meta
    # Record-specific fields
    date: datetime
    event: str
    status: str
    rssi: Optional[float] = None
    battery_voltage: Optional[float] = None
    snr: Optional[float] = None
    sensor_id: Optional[str] = None
    sensor_provider: Optional[str] = None



# API Response Models
class PaginatedResponse(BaseModel):
    total: int
    items: List[Any]

class LineListResponse(PaginatedResponse):
    items: List[Line]

class TrapListResponse(PaginatedResponse):
    items: List[Trap]

class TrapRecordListResponse(PaginatedResponse):
    items: List[TrapRecord]

# Query Parameter Models
class LineQueryParams(BaseModel):
    changed_since: Optional[datetime] = None
    changed_since_uuid: Optional[UUID] = None
    limit: int = 1000
    project: Optional[UUID] = None
    organisation: Optional[UUID] = None

class TrapQueryParams(BaseModel):
    changed_since: Optional[datetime] = None
    changed_since_uuid: Optional[UUID] = None
    limit: int = 1000
    project: Optional[UUID] = None
    organisation: Optional[UUID] = None
    line: Optional[UUID] = None

class TrapRecordQueryParams(BaseModel):
    changed_since: Optional[datetime] = None
    changed_before: Optional[datetime] = None
    limit: int = 1000
    offset: int = 0
    sort_order: str = "asc"
    organisation: Optional[UUID] = None
    trap: Optional[UUID] = None
    project: Optional[Union[List[UUID], UUID]] = None
    line: Optional[Union[List[UUID], UUID]] = None
    sort_column: str = "date"
    sensor_id: Optional[Union[List[str], str]] = None
    sensor_provider: Optional[Union[List[str], str]] = None
    battery_voltage_min: Optional[float] = Field(None, ge=0, le=50)
    battery_voltage_max: Optional[float] = Field(None, ge=0, le=50)
    snr_min: Optional[float] = None
    snr_max: Optional[float] = None
    rssi_min: Optional[float] = None
    rssi_max: Optional[float] = None
    event: Optional[List[str]] = None
    status: Optional[List[str]] = None

class Volunteer(BaseModel):
    name: str # The preferred name of the user
    preferences: str # A Json document recording preferences


