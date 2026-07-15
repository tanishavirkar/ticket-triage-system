from pydantic import BaseModel, Field

class TicketInput(BaseModel):
    """
    Pydantic model representing the input payload for an incoming support ticket.
    """
    subject: str = Field(..., description="The subject of the support ticket")
    body: str = Field(..., description="The main text body of the support ticket")

class TriageOutput(BaseModel):
    """
    Pydantic model representing the structured output triage assessment.
    """
    product_area: str = Field(..., description="The predicted product area or module related to the issue")
    issue_category: str = Field(..., description="The predicted issue category (e.g., Bug, How-To, Billing, etc.)")
    urgency: str = Field(..., description="The predicted urgency level (P1, P2, P3, P4)")
    reasoning: str = Field(..., description="Short explanation or reasoning justifying the triage decisions")
    matching_kb: str = Field(..., description="The matching article name or key content retrieved from the knowledge base")
    responder_team: str = Field(..., description="Suggested internal team to handle the ticket (e.g. Engineering, Billing, Customer Support)")
    draft_response: str = Field(..., description="A prepared draft response context for the customer based on KB context")
    confidence: float = Field(..., description="Confidence score indicating classification certainty (0.0 to 1.0)")
