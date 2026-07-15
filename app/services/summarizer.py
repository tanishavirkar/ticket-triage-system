import os
import json
import collections
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional
from openai import OpenAI
from app.config import settings
from app.schemas.summary import AccountSummaryResponse

class AccountSummarizerService:
    """
    Service for analyzing customer account health and churn risk using account metadata
    and recent support tickets (last 90 days).
    """
    def __init__(self, api_key: str = settings.openai_api_key, model_name: str = settings.openai_model_name):
        self.api_key = api_key
        self.model_name = model_name
        self._client = None
        
        # Load account database
        self.accounts_map = {}
        self.load_accounts()

        # Load tickets database grouped by account_id for O(1) lookups
        self.tickets_by_account = collections.defaultdict(list)
        self.load_tickets()

    @property
    def client(self) -> OpenAI:
        if not self.api_key:
            raise ValueError("OpenAI API key is missing. Please set OPENAI_API_KEY in your environment or .env file.")
        if self._client is None:
            self._client = OpenAI(api_key=self.api_key)
        return self._client

    def load_accounts(self) -> None:
        """
        Parses and loads accounts database into a fast memory map.
        """
        path = settings.accounts_file_path
        if not os.path.exists(path):
            print(f"Warning: Accounts database file missing at {path}")
            return

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            for acc in data:
                acc_id = acc.get("account_id")
                if acc_id:
                    self.accounts_map[acc_id] = acc

    def load_tickets(self) -> None:
        """
        Parses and loads all support tickets grouped by account_id.
        """
        path = settings.tickets_file_path
        if not os.path.exists(path):
            print(f"Warning: Tickets database file missing at {path}")
            return

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            for ticket in data:
                acc_id = ticket.get("account_id")
                if acc_id:
                    self.tickets_by_account[acc_id].append(ticket)

    def get_recent_tickets(self, account_id: str, reference_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """
        Filters and returns tickets for the given account created within the last 90 days.
        """
        # Default reference date to current datetime in UTC
        ref_dt = reference_date or datetime.now(timezone.utc)
        cutoff_dt = ref_dt - timedelta(days=90)
        
        account_tickets = self.tickets_by_account.get(account_id, [])
        recent_tickets = []
        
        for t in account_tickets:
            created_at_str = t.get("created_at")
            if not created_at_str:
                continue
            
            try:
                # Convert ISO string to timezone-aware datetime (replacing Z with UTC offset)
                created_dt = datetime.fromisoformat(created_at_str.replace("Z", "+00:00"))
                if created_dt >= cutoff_dt:
                    recent_tickets.append(t)
            except Exception as e:
                print(f"Warning: Failed to parse ticket creation timestamp '{created_at_str}': {e}")
                
        return recent_tickets

    def summarize_account_health(
        self, 
        account_id: str, 
        reference_date: Optional[datetime] = None
    ) -> AccountSummaryResponse:
        """
        Analyzes account health and risk factors to produce a validated AccountSummaryResponse.
        """
        # Look up customer profile
        account_data = self.accounts_map.get(account_id)
        if not account_data:
            raise KeyError(f"Customer account ID '{account_id}' not found in accounts database.")

        # Get recent tickets from the last 90 days
        recent_tickets = self.get_recent_tickets(account_id, reference_date=reference_date)

        # Fallback to mock generation if no live API key is set
        if not self.api_key:
            # Generate deterministic mock summary data matching customer profile health status
            is_at_risk = account_data.get("health_status") == "At Risk"
            return AccountSummaryResponse(
                account_id=account_id,
                company=account_data.get("company", "Unknown Company"),
                tam_name=account_data.get("tam", "Unassigned"),
                churn_risk_level="High" if is_at_risk else "Low",
                risk_factors=[
                    "Escalation note: " + ", ".join(account_data.get("escalation_notes", [])),
                    f"Found {len(recent_tickets)} recent support tickets within the 90-day window."
                ] if is_at_risk else ["No critical risk signals flagged."],
                tam_action_plan=[
                    f"Contact VP Primary Contact: {account_data.get('primary_contact', {}).get('name')} immediately.",
                    "Review integration connections and usage trend indicators."
                ] if is_at_risk else ["Maintain standard check-ins and review open tickets."],
                summary_reasoning=f"Mock health assessment: Trend is {account_data.get('usage_trend')} and status is {account_data.get('health_status')}."
            )

        # Format recent tickets into string context
        if recent_tickets:
            ticket_lines = []
            for t in recent_tickets:
                ticket_lines.append(
                    f"- Ticket ID: {t.get('ticket_id')}\n"
                    f"  Subject: {t.get('subject')}\n"
                    f"  Urgency: {t.get('urgency')} | Category: {t.get('category')} | Status: {t.get('status')}\n"
                    f"  Body: {t.get('body', '').strip()}"
                )
            recent_tickets_str = "\n\n".join(ticket_lines)
        else:
            recent_tickets_str = "No support tickets submitted in the last 90 days."

        # Template LLM prompts
        system_prompt = """You are a senior Technical Account Manager (TAM).

Your goal is to evaluate the health and churn risk of a customer account.

You receive:
- The customer account profile (ARR, seats, usage trend, NPS, active integrations, escalation notes).
- Recent support tickets submitted by this account in the last 90 days.

You must:
1. Evaluate the Churn Risk Level (Low, Medium, High).
2. Identify specific Churn Risk Factors based on escalation notes and recent ticket trends (e.g., repeating bugs, billing disputes, decreasing usage).
3. Formulate a TAM Action Plan (step-by-step mitigation items for the TAM to retain the customer).
4. Explain your summary reasoning.

You must ONLY use the provided account profile, escalation notes, and recent tickets.
Return ONLY valid JSON matching the schema.
"""

        user_prompt = f"""Account Profile

Company: {account_data.get('company')}
Plan Tier: {account_data.get('plan_tier')}
ARR (USD): {account_data.get('arr_usd')}
Licensed Seats: {account_data.get('seats_licensed')}
Active Seats: {account_data.get('seats_active')}
Health Trend Status: {account_data.get('health_status')}
Usage Trend: {account_data.get('usage_trend')}
NPS Score: {account_data.get('nps_score')}
Escalation Notes: {account_data.get('escalation_notes')}
Active Integrations: {account_data.get('integrations_active')}

Recent Tickets (Last 90 Days)

{recent_tickets_str}

Return JSON

{{
"account_id": "{account_id}",
"company": "{account_data.get('company')}",
"tam_name": "{account_data.get('tam')}",
"churn_risk_level": "",
"risk_factors": [],
"tam_action_plan": [],
"summary_reasoning": ""
}}"""

        # Call OpenAI Chat Completion with structured response parsing
        completion = self.client.beta.chat.completions.parse(
            model=self.model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format=AccountSummaryResponse,
            temperature=0.0
        )

        summary_decision = completion.choices[0].message.parsed
        return summary_decision
