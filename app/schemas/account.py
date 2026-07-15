from datetime import date
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field
from app.schemas.ticket import PlanTier

class HealthStatus(str, Enum):
    HEALTHY = "Healthy"
    AT_RISK = "At Risk"
    CHURNING = "Churning"
    NEW = "New"

class UsageTrend(str, Enum):
    INCREASING = "Increasing"
    STABLE = "Stable"
    DECLINING = "Declining"
    INACTIVE = "Inactive"

class Region(str, Enum):
    US_EAST = "US-East"
    US_WEST = "US-West"
    US_CENTRAL = "US-Central"
    EU_WEST = "EU-West"
    APAC = "APAC"

class PrimaryContact(BaseModel):
    name: str
    title: str

class Account(BaseModel):
    account_id: str
    company: str
    tam: str
    plan_tier: PlanTier
    arr_usd: int
    seats_licensed: int
    seats_active: int
    products: List[str] = Field(default_factory=list)
    health_status: HealthStatus
    usage_trend: UsageTrend
    open_tickets: int
    p1_tickets_last_30d: int
    customer_since: Optional[date] = None
    renewal_date: Optional[date] = None
    last_qbr_date: Optional[date] = None
    primary_contact: Optional[PrimaryContact] = None
    escalation_notes: List[str] = Field(default_factory=list)
    nps_score: Optional[int] = None
    last_login_days_ago: Optional[int] = None
    integrations_active: List[str] = Field(default_factory=list)
    region: Region
    industry: str
