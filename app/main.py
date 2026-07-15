from fastapi import FastAPI
from app.routers.triage import router as triage_router
from app.config import settings

app = FastAPI(
    title="AI-Powered Support Ticket Triage System",
    description="Automated support ticket categorization, prioritization, tagging, and routing using FAISS and OpenAI.",
    version="1.0.0",
)

# Register routers
app.include_router(triage_router)

@app.get("/", tags=["Health"])
def health_check():
    """
    Health check endpoint to verify server status.
    """
    return {
        "status": "healthy",
        "app_name": app.title,
        "version": app.version
    }
