# test_assess.py
import requests
import json

API_URL = "http://127.0.0.1:8080/assess"

payload = {
    "company_id": "COMP123",
    "financial_data": {
        "debt_to_equity": 1.5,
        "current_ratio": 1.2,
        "interest_coverage": 2.5,
        "revenue_growth": 0.05,
        "foreign_currency_exposure": 0.2,
        "commodity_exposure": 0.1,
        "system_downtime_hours": 20,
        "employee_turnover_rate": 0.1,
        "process_error_rate": 0.01,
        "top_supplier_concentration": 0.2,
        "security_incidents_year": 1,
        "regulatory_violations_year": 0,
        "compliance_audit_findings": 2,
        "sox_compliant": True,
        "gdpr_compliant": True,
        "basel_compliant": True,
        "pending_litigation": 0
    },
    "market_data": {
        "volatility": 0.2,
        "beta": 1.1
    },
    "compliance_requirements": ["SOX", "GDPR"],
    "include_rag_analysis": True
}

response = requests.post(API_URL, json=payload)

if response.status_code == 200:
    result = response.json()
    print(json.dumps(result, indent=2))
else:
    print(f"Error {response.status_code}: {response.text}")
