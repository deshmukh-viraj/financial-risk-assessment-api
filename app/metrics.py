# app/metrics.py
from prometheus_client import Counter, Histogram, Gauge

agent_requests = Counter('agent_requests_total', 'Total agent requests', ['agent_type'])
agent_response_time = Histogram('agent_response_seconds', 'Agent response time', ['agent_type'])
risk_scores = Gauge('risk_score_current', 'Current risk scores', ['risk_type'])
rag_queries = Counter('rag_queries_total', 'Total RAG queries')
api_requests = Counter('api_requests_total', 'Total API requests', ['endpoint'])
system_errors = Counter('system_errors_total', 'Total system errors', ['component'])
