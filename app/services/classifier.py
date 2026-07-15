from typing import List, Optional, Dict, Any
from openai import OpenAI
from app.config import settings
from app.schemas.schema import TicketInput, TriageOutput

class ClassifierService:
    """
    Service for classifying tickets using OpenAI's Chat Completions structured outputs.
    Configured with Senior Tier-2 Support Engineer instructions.
    """
    def __init__(self, api_key: str = settings.openai_api_key, model_name: str = settings.openai_model_name):
        self.api_key = api_key
        self.model_name = model_name
        self._client = None

    @property
    def client(self) -> OpenAI:
        if not self.api_key:
            raise ValueError("OpenAI API key is missing. Please set OPENAI_API_KEY in your environment or .env file.")
        if self._client is None:
            self._client = OpenAI(api_key=self.api_key)
        return self._client

    def classify_ticket(
        self,
        request: TicketInput,
        relevant_kb_docs: Optional[List[Dict[str, Any]]] = None
    ) -> TriageOutput:
        """
        Runs LLM classification on an incoming ticket using only the provided ticket details
        and knowledge base articles (RAG context).
        """
        # Format retrieved KB articles
        if relevant_kb_docs:
            kb_list = []
            for doc in relevant_kb_docs:
                kb_list.append(doc.get('text', '').strip())
            kb_str = "\n\n".join(kb_list)
        else:
            kb_str = "No documentation provided."

        system_prompt = """You are a senior Tier-2 Support Engineer.

You receive customer support tickets.

You must:
1. Determine Product Area
2. Determine Issue Category
3. Determine Priority:
   P1 = Critical production outage
   P2 = Major issue
   P3 = Normal support issue
   P4 = Minor issue
4. Explain reasoning.
5. Determine whether the issue matches the supplied documentation. Under the 'matching_kb' field, summarize if it matches, and if the documentation does not match, explicitly write 'Documentation does not match'.
6. Recommend the responder team.
7. Draft the first customer response.

You must ONLY use the provided ticket and documentation.
If documentation does not match, explicitly say so.
Return ONLY valid JSON matching the schema.
"""

        # Format user prompt exactly according to user layout
        user_prompt = f"""Ticket

Subject

{request.subject}

Body

{request.body}

Relevant Documentation

{kb_str}

Return JSON

{{
"product_area":"",
"issue_category":"",
"urgency":"",
"reasoning":"",
"matching_kb":"",
"responder_team":"",
"draft_response":"",
"confidence":0.0
}}"""

        # Call OpenAI Chat Completion with structured response parsing
        completion = self.client.beta.chat.completions.parse(
            model=self.model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format=TriageOutput,
            temperature=0.0  # Zero temperature for deterministic engineering decisions
        )

        triage_decision = completion.choices[0].message.parsed
        return triage_decision
