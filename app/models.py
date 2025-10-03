# app/models.py
from enum import Enum
from datetime import datetime
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field

class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class RiskAssessmentRequest(BaseModel):
    company_id: str
    financial_data: Dict[str, Any]
    market_data: Optional[Dict[str, Any]] = None
    compliance_requirements: Optional[List[str]] = None
    include_rag_analysis: bool = True

class RiskScore(BaseModel):
    risk_type: str
    score: float = Field(ge=0, le=1)
    level: RiskLevel
    factors: List[str]
    confidence: float = Field(ge=0, le=1)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ComprehensiveRiskAssessment(BaseModel):
    company_id: str
    credit_risk: RiskScore
    market_risk: RiskScore
    operational_risk: RiskScore
    compliance_risk: RiskScore
    overall_risk_score: float
    overall_risk_level: RiskLevel
    recommendations: List[str]
    assessment_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
