# tests/test_api.py
import pytest
from fastapi.testclient import TestClient
from app.main import app, orchestrator

client = TestClient(app)

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert "status" in r.json()

@pytest.fixture(autouse=True)
def patch_orchestrator(monkeypatch):
    async def fake_assess(request):
        # minimal fake ComprehensiveRiskAssessment-like dict/object
        from app.models import ComprehensiveRiskAssessment, RiskScore, RiskLevel
        cs = RiskScore(risk_type="credit", score=0.1, level=RiskLevel.LOW, factors=[], confidence=0.9)
        ms = RiskScore(risk_type="market", score=0.2, level=RiskLevel.MEDIUM, factors=[], confidence=0.8)
        os = RiskScore(risk_type="operational", score=0.1, level=RiskLevel.LOW, factors=[], confidence=0.75)
        coms = RiskScore(risk_type="compliance", score=0.05, level=RiskLevel.LOW, factors=[], confidence=0.9)
        return ComprehensiveRiskAssessment(
            company_id=request.company_id,
            credit_risk=cs, market_risk=ms, operational_risk=os, compliance_risk=coms,
            overall_risk_score=0.125, overall_risk_level=RiskLevel.LOW,
            recommendations=[], assessment_id="RA-TEST"
        )
    monkeypatch.setattr(orchestrator, "assess_risk", fake_assess)
    yield

def test_assess_endpoint():
    payload = {
        "company_id": "testco",
        "financial_data": {},
        "market_data": {},
        "compliance_requirements": []
    }
    r = client.post("/assess", json=payload)
    assert r.status_code == 200
    j = r.json()
    assert j["company_id"] == "testco"
    assert "assessment_id" in j
