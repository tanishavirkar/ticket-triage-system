from fastapi import APIRouter, Depends, HTTPException
from app.schemas.schema import TicketInput, TriageOutput
from app.services.triage_service import TriageService

router = APIRouter(prefix="/api/triage", tags=["Triage"])

# Single service instance cache to avoid reloading FAISS indices on every request
_triage_service_instance = None

def get_triage_service() -> TriageService:
    """
    Dependency provider to retrieve cached TriageService instances.
    """
    global _triage_service_instance
    if _triage_service_instance is None:
        _triage_service_instance = TriageService()
    return _triage_service_instance


@router.post("", response_model=TriageOutput, summary="Triage an incoming support ticket")
def triage_ticket(
    request: TicketInput, 
    service: TriageService = Depends(get_triage_service)
) -> TriageOutput:
    """
    Endpoint that processes the incoming support ticket text (and account context)
    to categorize, prioritize, tag, and route the ticket using semantic search (RAG) and LLMs.
    """
    try:
        return service.triage(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Triage processing failed: {str(e)}")

