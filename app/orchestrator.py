# app/orchestrator.py
from typing import Dict, Any, List
from typing_extensions import TypedDict
from app.models import RiskAssessmentRequest, ComprehensiveRiskAssessment
from app.rag_pipeline import RAGPipeline
from app.agents import CreditRiskAgent, MarketRiskAgent, OperationalRiskAgent, ComplianceRiskAgent
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from datetime import datetime
from app.metrics import risk_scores

class AgentState(TypedDict):
    messages: List[Any]
    company_id: str
    financial_data: Dict[str, Any]
    market_data: Dict[str, Any]
    compliance_requirements: List[str]
    credit_risk: Any
    market_risk: Any
    operational_risk: Any
    compliance_risk: Any
    rag_context: Any
    iteration: int
    final_assessment: Any

class RiskAssessmentOrchestrator:
    def __init__(self, rag_pipeline: RAGPipeline):
        self.rag_pipeline = rag_pipeline
        self.credit_agent = CreditRiskAgent()
        self.market_agent = MarketRiskAgent()
        self.operational_agent = OperationalRiskAgent()
        self.compliance_agent = ComplianceRiskAgent()
        self.memory = MemorySaver()
        self.graph = self._build_graph()

    def _build_graph(self):
        workflow = StateGraph(AgentState)
        workflow.add_node("rag_retrieval", self.rag_retrieval_node)
        workflow.add_node("credit_analysis", self.credit_analysis_node)
        workflow.add_node("market_analysis", self.market_analysis_node)
        workflow.add_node("operational_analysis", self.operational_analysis_node)
        workflow.add_node("compliance_analysis", self.compliance_analysis_node)
        workflow.add_node("risk_synthesis", self.risk_synthesis_node)

        workflow.set_entry_point("rag_retrieval")
        workflow.add_edge("rag_retrieval", "credit_analysis")
        workflow.add_edge("credit_analysis", "market_analysis")
        workflow.add_edge("market_analysis", "operational_analysis")
        workflow.add_edge("operational_analysis", "compliance_analysis")
        workflow.add_edge("compliance_analysis", "risk_synthesis")
        workflow.add_edge("risk_synthesis", END)

        return workflow.compile(checkpointer=self.memory)

    def rag_retrieval_node(self, state: AgentState) -> Dict:
        company_id = state["company_id"]
        query = f"Financial risk assessment for company {company_id} including credit, market, operational, and compliance risks"
        context = self.rag_pipeline.query(query)
        return {"rag_context": context}

    def credit_analysis_node(self, state: AgentState) -> Dict:
        credit_risk = self.credit_agent.analyze(state)
        return {"credit_risk": credit_risk}

    def market_analysis_node(self, state: AgentState) -> Dict:
        market_risk = self.market_agent.analyze(state)
        return {"market_risk": market_risk}

    def operational_analysis_node(self, state: AgentState) -> Dict:
        operational_risk = self.operational_agent.analyze(state)
        return {"operational_risk": operational_risk}

    def compliance_analysis_node(self, state: AgentState) -> Dict:
        compliance_risk = self.compliance_agent.analyze(state)
        return {"compliance_risk": compliance_risk}

    def risk_synthesis_node(self, state: AgentState) -> Dict:
        credit_risk = state["credit_risk"]
        market_risk = state["market_risk"]
        operational_risk = state["operational_risk"]
        compliance_risk = state["compliance_risk"]

        weights = {"credit": 0.3, "market": 0.25, "operational": 0.2, "compliance": 0.25}
        overall_score = (
            credit_risk.score * weights["credit"] +
            market_risk.score * weights["market"] +
            operational_risk.score * weights["operational"] +
            compliance_risk.score * weights["compliance"]
        )

        if overall_score < 0.3:
            overall_level = credit_risk.level.__class__.LOW
        elif overall_score < 0.6:
            overall_level = credit_risk.level.__class__.MEDIUM
        elif overall_score < 0.85:
            overall_level = credit_risk.level.__class__.HIGH
        else:
            overall_level = credit_risk.level.__class__.CRITICAL

        recommendations = self._generate_recommendations(credit_risk, market_risk, operational_risk, compliance_risk)
        assessment = ComprehensiveRiskAssessment(
            company_id=state["company_id"],
            credit_risk=credit_risk,
            market_risk=market_risk,
            operational_risk=operational_risk,
            compliance_risk=compliance_risk,
            overall_risk_score=overall_score,
            overall_risk_level=overall_level,
            recommendations=recommendations,
            assessment_id=f"RA-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        )
        risk_scores.labels(risk_type="overall").set(overall_score)
        return {"final_assessment": assessment}

    def _generate_recommendations(self, credit_risk, market_risk, operational_risk, compliance_risk):
        recommendations = []
        if credit_risk.level in [credit_risk.level.__class__.HIGH, credit_risk.level.__class__.CRITICAL]:
            recommendations.append("Urgent: Improve debt-to-equity ratio through debt reduction or equity financing")
            recommendations.append("Enhance cash flow management and working capital optimization")
        elif credit_risk.level == credit_risk.level.__class__.MEDIUM:
            recommendations.append("Monitor liquidity ratios closely and maintain adequate cash reserves")

        if market_risk.level in [market_risk.level.__class__.HIGH, market_risk.level.__class__.CRITICAL]:
            recommendations.append("Implement hedging strategies for currency and commodity exposures")
            recommendations.append("Diversify market exposure to reduce systematic risk")
        elif market_risk.level == market_risk.level.__class__.MEDIUM:
            recommendations.append("Consider partial hedging of major market exposures")

        if operational_risk.level in [operational_risk.level.__class__.HIGH, operational_risk.level.__class__.CRITICAL]:
            recommendations.append("Strengthen IT infrastructure and cybersecurity measures")
            recommendations.append("Implement business continuity and disaster recovery plans")
            recommendations.append("Diversify supplier base to reduce concentration risk")
        elif operational_risk.level == operational_risk.level.__class__.MEDIUM:
            recommendations.append("Review and update operational procedures regularly")

        if compliance_risk.level in [compliance_risk.level.__class__.HIGH, compliance_risk.level.__class__.CRITICAL]:
            recommendations.append("Immediate compliance audit and remediation required")
            recommendations.append("Strengthen compliance monitoring and reporting systems")
        elif compliance_risk.level == compliance_risk.level.__class__.MEDIUM:
            recommendations.append("Enhance compliance training programs")

        return recommendations

    async def assess_risk(self, request: RiskAssessmentRequest) -> ComprehensiveRiskAssessment:
        initial_state: AgentState = {
            "messages": [],
            "company_id": request.company_id,
            "financial_data": request.financial_data,
            "market_data": request.market_data or {},
            "compliance_requirements": request.compliance_requirements or [],
            "credit_risk": None,
            "market_risk": None,
            "operational_risk": None,
            "compliance_risk": None,
            "rag_context": None,
            "iteration": 0,
            "final_assessment": None
        }
        config = {"configurable": {"thread_id": request.company_id}}
        result = await self.graph.ainvoke(initial_state, config)
        return result["final_assessment"]
