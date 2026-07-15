from fastapi import FastAPI, Depends, HTTPException
from app.schemas.schema import TicketInput, TriageOutput
from app.schemas.summary import AccountSummaryResponse
from app.services.triage_service import TriageService
from app.services.summarizer import AccountSummarizerService

app = FastAPI(
    title="AI Support Ticket Triage System",
    description="FastAPI service for automated support ticket triage using FAISS RAG and OpenAI.",
    version="1.0.0"
)

# Caches to avoid reloading database and FAISS indexes on every HTTP request
_triage_service_instance = None
_summarizer_service_instance = None

def get_triage_service() -> TriageService:
    global _triage_service_instance
    if _triage_service_instance is None:
        _triage_service_instance = TriageService()
    return _triage_service_instance

def get_summarizer_service() -> AccountSummarizerService:
    global _summarizer_service_instance
    if _summarizer_service_instance is None:
        _summarizer_service_instance = AccountSummarizerService()
    return _summarizer_service_instance

@app.post("/triage", response_model=TriageOutput, summary="Triage an incoming support ticket")
def triage_endpoint(
    ticket: TicketInput,
    service: TriageService = Depends(get_triage_service)
) -> TriageOutput:
    """
    Triage an incoming support ticket.

    Workflow:
    Input ticket -> Retrieve relevant KB -> Call LLM -> Return structured output
    """
    try:
        return service.triage(ticket)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Triage processing failed: {str(e)}")

@app.get(
    "/accounts/{account_id}/health-summary",
    response_model=AccountSummaryResponse,
    summary="Retrieve account health summary and churn risk analysis"
)
def get_account_health_summary(
    account_id: str,
    service: AccountSummarizerService = Depends(get_summarizer_service)
) -> AccountSummaryResponse:
    """
    Analyzes and summarizes the customer account profile health trend, NPS, and support ticket history
    to evaluate churn risk and recommend mitigation action items.
    """
    try:
        return service.summarize_account_health(account_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Account health summary evaluation failed: {str(e)}")

@app.get("/", tags=["HealthCheck"])
def health_check():
    """
    Health check endpoint to verify server status.
    """
    return {
        "status": "healthy",
        "app_name": app.title,
        "version": app.version
    }
