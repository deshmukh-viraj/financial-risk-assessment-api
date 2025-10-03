# app/config.py
import os
import logging

class Config:
    """Central configuration for the system"""
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "your-api-key")
    VECTOR_DB_PATH = os.getenv("VECTOR_DB_PATH", "./vector_store")
    PROMETHEUS_PORT = int(os.getenv("PROMETHEUS_PORT", "8000"))
    API_PORT = int(os.getenv("API_PORT", "8080"))
    HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
    MAX_ITERATIONS = 10
    RISK_THRESHOLDS = {
        "low": 0.3,
        "medium": 0.6,
        "high": 0.85,
        "critical": 1.0
    }

# logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("risk_assessment_api")
