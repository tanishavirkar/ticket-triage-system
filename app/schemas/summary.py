from typing import List
from pydantic import BaseModel, Field

class AccountSummaryResponse(BaseModel):
    """
    Pydantic schema representing the structured output for a customer account's health
    and churn-risk assessment.
    """
    account_id: str = Field(..., description="The unique ID of the customer account")
    company: str = Field(..., description="The name of the customer company")
    tam_name: str = Field(..., description="The name of the assigned Technical Account Manager")
    churn_risk_level: str = Field(..., description="The evaluated churn risk level: 'Low', 'Medium', or 'High'")
    risk_factors: List[str] = Field(..., description="Specific indicators derived from escalation notes and recent ticket trends")
    tam_action_plan: List[str] = Field(..., description="Step-by-step mitigation items recommended for the TAM to retain the customer")
    summary_reasoning: str = Field(..., description="A brief summary explanation justifying the risk assessment")
