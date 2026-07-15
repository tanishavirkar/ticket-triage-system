from typing import List, Optional
from pydantic import BaseModel, Field
from app.schemas.ticket import TicketCategory, TicketUrgency

class TriageRequest(BaseModel):
    subject: str = Field(..., description="Subject of the support ticket")
    body: str = Field(..., description="Full body/text of the support ticket")
    account_id: Optional[str] = Field(None, description="Optional account ID of the customer submitting the ticket")

class TriageResponse(BaseModel):
    ticket_id: Optional[str] = Field(None, description="Generated or assigned ticket ID")
    category: TicketCategory = Field(..., description="Predicted issue category")
    urgency: TicketUrgency = Field(..., description="Predicted issue urgency level (P1-P4)")
    confidence: float = Field(..., description="Confidence score for the triage decision (0.0 to 1.0)")
    suggested_tags: List[str] = Field(default_factory=list, description="Recommended tags for the ticket")
    suggested_agent: Optional[str] = Field(None, description="Suggested support agent name based on routing rules")
    reasoning: str = Field(..., description="Brief explanation/rationale behind the triage decisions")
    similar_tickets: List[str] = Field(default_factory=list, description="List of similar historical ticket IDs retrieved")
    relevant_kb_articles: List[str] = Field(default_factory=list, description="Titles/paths of relevant knowledge base articles retrieved")
