from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field

class TicketCategory(str, Enum):
    BUG = "Bug"
    FEATURE_REQUEST = "Feature Request"
    HOW_TO = "How-To"
    PERFORMANCE = "Performance"
    BILLING = "Billing"
    INTEGRATION = "Integration"
    ONBOARDING = "Onboarding"
    DATA_LOSS = "Data Loss"

class TicketUrgency(str, Enum):
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"
    P4 = "P4"

class TicketStatus(str, Enum):
    OPEN = "Open"
    IN_PROGRESS = "In Progress"
    PENDING_CUSTOMER = "Pending Customer"
    RESOLVED = "Resolved"
    CLOSED = "Closed"

class PlanTier(str, Enum):
    STARTER = "Starter"
    PROFESSIONAL = "Professional"
    BUSINESS = "Business"
    ENTERPRISE = "Enterprise"

class TicketChannel(str, Enum):
    EMAIL = "email"
    PORTAL = "portal"
    CHAT = "chat"
    PHONE = "phone"

class Ticket(BaseModel):
    ticket_id: str
    account_id: Optional[str] = None
    company: Optional[str] = None
    subject: str
    body: str
    product: Optional[str] = None
    product_area: Optional[str] = None
    category: TicketCategory
    urgency: TicketUrgency
    status: TicketStatus
    plan_tier: PlanTier
    assigned_agent: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    tags: List[str] = Field(default_factory=list)
    channel: TicketChannel
    satisfaction_score: Optional[int] = None
