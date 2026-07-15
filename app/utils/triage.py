import json
from openai import OpenAI
from pydantic import ValidationError
from app.config import settings
from app.schemas.schema import TicketInput, TriageOutput
from app.utils.retriever import retrieve

def triage_ticket(ticket: TicketInput) -> TriageOutput:
    """
    Orchestrates the support ticket triage workflow:
    Input ticket -> Retrieve KB chunks -> Construct prompt -> Call OpenAI -> Validate using Pydantic -> Return object

    If JSON parsing or Pydantic validation fails, it retries exactly once.
    If the second attempt still fails, it raises an exception.
    """
    # 1. Retrieve the top 3 relevant KB articles
    ticket_text = f"Subject: {ticket.subject}\nBody: {ticket.body}"
    kb_results = retrieve(ticket_text, k=3)
    
    # Format documentation chunks
    if kb_results:
        kb_chunks_str = "\n\n".join([r.get("text", "").strip() for r in kb_results])
    else:
        kb_chunks_str = "No documentation provided."

    # 2. Construct the prompt matching Senior Tier-2 guidelines
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

    user_prompt = f"""Ticket

Subject

{ticket.subject}

Body

{ticket.body}

Relevant Documentation

{kb_chunks_str}

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

    # 3. Establish OpenAI connection config
    api_key = settings.openai_api_key
    if not api_key:
        raise ValueError("OpenAI API key is missing. Please set OPENAI_API_KEY in your environment or .env file.")
        
    client = OpenAI(api_key=api_key)
    model = settings.openai_model_name

    def execute_triage_call() -> TriageOutput:
        # Call OpenAI Chat Completion with JSON mode enabled to guarantee JSON syntax
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.0
        )
        
        raw_json_content = response.choices[0].message.content
        if not raw_json_content:
            raise ValueError("OpenAI returned an empty response")

        # Parse raw string content to dictionary
        parsed_data = json.loads(raw_json_content)

        # Validate structured dictionary using Pydantic model
        validated_output = TriageOutput(**parsed_data)
        return validated_output

    # 4. Execute with retry mechanism
    try:
        # First attempt
        return execute_triage_call()
    except (ValidationError, json.JSONDecodeError, Exception) as err:
        print(f"Warning: Triage parsing/validation failed on first attempt: {err}. Retrying once...")
        try:
            # Second attempt (retry once)
            return execute_triage_call()
        except Exception as retry_err:
            # If it still fails, raise a RuntimeError exception
            raise RuntimeError(
                f"Triage workflow failed validation after retry. "
                f"Original error: {err}. Retry error: {retry_err}"
            ) from retry_err
