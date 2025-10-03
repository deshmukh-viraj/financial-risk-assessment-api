# app/agents.py
from typing import Any, Dict, List
from app.models import RiskScore, RiskLevel
from app.metrics import agent_requests, agent_response_time, risk_scores, system_errors
from app.config import Config
from langchain_core.messages import HumanMessage
from langchain_groq import ChatGroq
import json
from datetime import datetime

class BaseRiskAgent:
    def __init__(self, agent_type: str):
        self.agent_type = agent_type
        self.llm = ChatGroq(temperature=0.6, model="qwen/qwen3-32b", groq_api_key=Config.GROQ_API_KEY)

    def analyze(self, state: Dict[str, Any]) -> RiskScore:
        raise NotImplementedError

class CreditRiskAgent(BaseRiskAgent):
    def __init__(self):
        super().__init__("credit_risk")

    @agent_response_time.labels(agent_type="credit").time()
    def analyze(self, state: Dict[str, Any]) -> RiskScore:
        agent_requests.labels(agent_type="credit").inc()

        financial_data = state["financial_data"]
        rag_context = state.get("rag_context", "")

        debt_to_equity = financial_data.get("debt_to_equity", 0)
        current_ratio = financial_data.get("current_ratio", 1)
        interest_coverage = financial_data.get("interest_coverage", 1)
        revenue_growth = financial_data.get("revenue_growth", 0)

        score = 0.0
        factors: List[str] = []

        if debt_to_equity > 2:
            score += 0.3
            factors.append("High debt-to-equity ratio")
        elif debt_to_equity > 1:
            score += 0.15
            factors.append("Moderate debt-to-equity ratio")

        if current_ratio < 1:
            score += 0.25
            factors.append("Poor liquidity position")
        elif current_ratio < 1.5:
            score += 0.1
            factors.append("Moderate liquidity")

        if interest_coverage < 1.5:
            score += 0.25
            factors.append("Weak interest coverage")
        elif interest_coverage < 3:
            score += 0.1
            factors.append("Moderate interest coverage")

        if revenue_growth < -0.1:
            score += 0.2
            factors.append("Declining revenue")
        elif revenue_growth < 0:
            score += 0.1
            factors.append("Stagnant revenue growth")

        prompt = f"""
        Analyze credit risk based on:
        Financial Data: {json.dumps(financial_data, indent=2)}
        Historical Context: {rag_context[:1000]}

        Provide additional risk factors and adjust the score if needed.
        Current preliminary score: {score}
        """

        try:
            # Keep previous invocation style; adapt if your langchain/langopenai version differs
            _ = self.llm.invoke([HumanMessage(content=prompt)])
            score = min(1.0, score * 1.1)
        except Exception as e:
            system_errors.labels(component="credit_agent_llm").inc()

        level = self._determine_risk_level(score)
        risk_scores.labels(risk_type="credit").set(score)

        return RiskScore(risk_type="credit", score=score, level=level, factors=factors, confidence=0.85)

    def _determine_risk_level(self, score: float) -> RiskLevel:
        if score < Config.RISK_THRESHOLDS["low"]:
            return RiskLevel.LOW
        elif score < Config.RISK_THRESHOLDS["medium"]:
            return RiskLevel.MEDIUM
        elif score < Config.RISK_THRESHOLDS["high"]:
            return RiskLevel.HIGH
        else:
            return RiskLevel.CRITICAL

class MarketRiskAgent(BaseRiskAgent):
    def __init__(self):
        super().__init__("market_risk")

    @agent_response_time.labels(agent_type="market").time()
    def analyze(self, state: Dict[str, Any]) -> RiskScore:
        agent_requests.labels(agent_type="market").inc()
        market_data = state.get("market_data", {})
        financial_data = state["financial_data"]

        score = 0.0
        factors: List[str] = []

        volatility = market_data.get("volatility", 0)
        if volatility > 0.3:
            score += 0.25
            factors.append("High market volatility")
        elif volatility > 0.2:
            score += 0.15
            factors.append("Moderate market volatility")

        beta = market_data.get("beta", 1.0)
        if beta > 1.5:
            score += 0.2
            factors.append("High systematic risk (beta > 1.5)")
        elif beta > 1.2:
            score += 0.1
            factors.append("Above-average systematic risk")

        fx_exposure = financial_data.get("foreign_currency_exposure", 0)
        if fx_exposure > 0.5:
            score += 0.2
            factors.append("Significant foreign currency exposure")
        elif fx_exposure > 0.3:
            score += 0.1
            factors.append("Moderate foreign currency exposure")

        commodity_exposure = financial_data.get("commodity_exposure", 0)
        if commodity_exposure > 0.4:
            score += 0.15
            factors.append("High commodity price risk")

        level = self._determine_risk_level(score)
        risk_scores.labels(risk_type="market").set(score)
        return RiskScore(risk_type="market", score=score, level=level, factors=factors, confidence=0.8)

    def _determine_risk_level(self, score: float) -> RiskLevel:
        if score < Config.RISK_THRESHOLDS["low"]:
            return RiskLevel.LOW
        elif score < Config.RISK_THRESHOLDS["medium"]:
            return RiskLevel.MEDIUM
        elif score < Config.RISK_THRESHOLDS["high"]:
            return RiskLevel.HIGH
        else:
            return RiskLevel.CRITICAL

class OperationalRiskAgent(BaseRiskAgent):
    def __init__(self):
        super().__init__("operational_risk")

    @agent_response_time.labels(agent_type="operational").time()
    def analyze(self, state: Dict[str, Any]) -> RiskScore:
        agent_requests.labels(agent_type="operational").inc()
        financial_data = state["financial_data"]

        score = 0.0
        factors: List[str] = []

        system_downtime = financial_data.get("system_downtime_hours", 0)
        if system_downtime > 100:
            score += 0.2
            factors.append("Significant IT system downtime")
        elif system_downtime > 50:
            score += 0.1
            factors.append("Moderate IT system issues")

        turnover_rate = financial_data.get("employee_turnover_rate", 0)
        if turnover_rate > 0.25:
            score += 0.15
            factors.append("High employee turnover")
        elif turnover_rate > 0.15:
            score += 0.08
            factors.append("Above-average employee turnover")

        process_error_rate = financial_data.get("process_error_rate", 0)
        if process_error_rate > 0.05:
            score += 0.2
            factors.append("High process error rate")
        elif process_error_rate > 0.02:
            score += 0.1
            factors.append("Moderate process errors")

        supplier_concentration = financial_data.get("top_supplier_concentration", 0)
        if supplier_concentration > 0.5:
            score += 0.25
            factors.append("High supplier concentration risk")
        elif supplier_concentration > 0.3:
            score += 0.12
            factors.append("Moderate supplier dependency")

        security_incidents = financial_data.get("security_incidents_year", 0)
        if security_incidents > 5:
            score += 0.3
            factors.append("Multiple cybersecurity incidents")
        elif security_incidents > 2:
            score += 0.15
            factors.append("Some cybersecurity concerns")

        level = self._determine_risk_level(score)
        risk_scores.labels(risk_type="operational").set(score)
        return RiskScore(risk_type="operational", score=score, level=level, factors=factors, confidence=0.75)

    def _determine_risk_level(self, score: float) -> RiskLevel:
        if score < Config.RISK_THRESHOLDS["low"]:
            return RiskLevel.LOW
        elif score < Config.RISK_THRESHOLDS["medium"]:
            return RiskLevel.MEDIUM
        elif score < Config.RISK_THRESHOLDS["high"]:
            return RiskLevel.HIGH
        else:
            return RiskLevel.CRITICAL

class ComplianceRiskAgent(BaseRiskAgent):
    def __init__(self):
        super().__init__("compliance_risk")

    @agent_response_time.labels(agent_type="compliance").time()
    def analyze(self, state: Dict[str, Any]) -> RiskScore:
        agent_requests.labels(agent_type="compliance").inc()
        financial_data = state["financial_data"]
        compliance_requirements = state.get("compliance_requirements", [])

        score = 0.0
        factors: List[str] = []

        violations = financial_data.get("regulatory_violations_year", 0)
        if violations > 3:
            score += 0.35
            factors.append("Multiple regulatory violations")
        elif violations > 1:
            score += 0.2
            factors.append("Some regulatory violations")
        elif violations == 1:
            score += 0.1
            factors.append("Minor regulatory violation")

        audit_findings = financial_data.get("compliance_audit_findings", 0)
        if audit_findings > 10:
            score += 0.25
            factors.append("Significant compliance audit findings")
        elif audit_findings > 5:
            score += 0.15
            factors.append("Moderate audit findings")

        for requirement in compliance_requirements:
            if requirement == "SOX" and not financial_data.get("sox_compliant", True):
                score += 0.2
                factors.append("SOX compliance issues")
            elif requirement == "GDPR" and not financial_data.get("gdpr_compliant", True):
                score += 0.15
                factors.append("GDPR compliance gaps")
            elif requirement == "Basel III" and not financial_data.get("basel_compliant", True):
                score += 0.25
                factors.append("Basel III non-compliance")

        litigation_cases = financial_data.get("pending_litigation", 0)
        if litigation_cases > 5:
            score += 0.2
            factors.append("Significant pending litigation")
        elif litigation_cases > 2:
            score += 0.1
            factors.append("Some pending litigation")

        level = self._determine_risk_level(score)
        risk_scores.labels(risk_type="compliance").set(score)
        return RiskScore(risk_type="compliance", score=score, level=level, factors=factors, confidence=0.9)

    def _determine_risk_level(self, score: float) -> RiskLevel:
        if score < Config.RISK_THRESHOLDS["low"]:
            return RiskLevel.LOW
        elif score < Config.RISK_THRESHOLDS["medium"]:
            return RiskLevel.MEDIUM
        elif score < Config.RISK_THRESHOLDS["high"]:
            return RiskLevel.HIGH
        else:
            return RiskLevel.CRITICAL
