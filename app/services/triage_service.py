from app.schemas.schema import TicketInput, TriageOutput
from app.utils.vector_store import load_index
from app.utils.triage import triage_ticket

class TriageService:
    """
    Service class orchestrating the support ticket triage pipeline.
    """
    def __init__(self):
        # Load global FAISS index on initialization to avoid loading on demand
        try:
            load_index()
        except Exception as e:
            print(f"Warning: Failed to load FAISS index during startup: {e}. Run build_index.py to compile it.")

    def triage(self, ticket: TicketInput) -> TriageOutput:
        """
        Pipeline:
        Ticket -> Retrieve relevant KB -> Call LLM -> Return structured output
        """
        return triage_ticket(ticket)

    def process_ticket(self, ticket: TicketInput) -> TriageOutput:
        """
        Alias for backwards compatibility with the FastAPI router.
        """
        return self.triage(ticket)

def triage(ticket: TicketInput) -> TriageOutput:
    """
    Module-level function exposing the ticket triage pipeline.
    Returns a validated TriageOutput Pydantic object.
    """
    # Instantiate service which ensures global indices are loaded, and run triage
    service = TriageService()
    return service.triage(ticket)
