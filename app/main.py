# app/main.py
import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from app.config import Config, logger
from app.rag_pipeline import RAGPipeline
from app.orchestrator import RiskAssessmentOrchestrator
from app.mcp_server import MCPServer
from app.metrics import api_requests, system_errors
import prometheus_client
from prometheus_client import start_http_server
from app.models import RiskAssessmentRequest, ComprehensiveRiskAssessment

app = FastAPI(title="Financial Risk Assessment API", version="1.0.0", openapi_url=None)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components (singletons)
rag_pipeline = RAGPipeline(Config.VECTOR_DB_PATH)
orchestrator = RiskAssessmentOrchestrator(rag_pipeline)
mcp_server = MCPServer()

@app.post("/assess", response_model=ComprehensiveRiskAssessment)
async def assess_risk_endpoint(request: RiskAssessmentRequest, background_tasks: BackgroundTasks):
    api_requests.labels(endpoint="/assess").inc()
    try:
        assessment = await orchestrator.assess_risk(request)
        background_tasks.add_task(mcp_server.log_assessment, assessment)
        return assessment
    except Exception as e:
        logger.error(f"Error in /assess: {e}")
        system_errors.labels(component="api").inc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/metrics")
async def metrics_endpoint():
    data = prometheus_client.generate_latest()
    return PlainTextResponse(content=data.decode("utf-8"), media_type="text/plain; version=0.0.4")

@app.get("/health")
async def health():
    try:
        system_metrics = mcp_server.get_system_metrics()
    except Exception:
        system_metrics = {"system_health": "degraded"}
    return {"status": "ok", "metrics": system_metrics}

@app.on_event("startup")
async def startup_event():
    try:
        start_http_server(Config.PROMETHEUS_PORT)
        logger.info(f"Prometheus server started on port {Config.PROMETHEUS_PORT}")
    except Exception as e:
        logger.warning(f"Failed to start prometheus http server: {e}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=Config.API_PORT)
