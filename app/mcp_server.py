# app/mcp_server.py
import json
import os
from datetime import datetime
from typing import List, Dict
from app.config import logger
from app.metrics import system_errors


class MCPServer:
    def __init__(self, storage_file: str = "data/assessments.json"):
        self.assessments = {}  # in-memory store: {assessment_id: data}
        self.company_map = {}  # {company_id: [assessment_ids]}
        self.storage_file = storage_file

        # Ensure folder exists
        os.makedirs(os.path.dirname(storage_file), exist_ok=True)

        # Load existing file if available
        if os.path.exists(storage_file):
            try:
                with open(storage_file, "r") as f:
                    data = json.load(f)
                    self.assessments = data.get("assessments", {})
                    self.company_map = data.get("company_map", {})
                logger.info("Loaded existing assessments from file storage")
            except Exception as e:
                logger.warning(f"Could not load existing assessments: {e}")

    def _persist(self):
        """Save assessments to disk for persistence across restarts"""
        try:
            with open(self.storage_file, "w") as f:
                json.dump(
                    {
                        "assessments": self.assessments,
                        "company_map": self.company_map,
                    },
                    f,
                    indent=2,
                    default=str,
                )
        except Exception as e:
            logger.error(f"Failed to persist assessments: {e}")
            system_errors.labels(component="mcp_server").inc()

    async def log_assessment(self, assessment):
        """Save assessment to memory and file"""
        try:
            assessment_data = assessment.dict()
            assessment_data["timestamp"] = assessment_data["timestamp"].isoformat()
            self.assessments[assessment.assessment_id] = assessment_data

            if assessment.company_id not in self.company_map:
                self.company_map[assessment.company_id] = []
            self.company_map[assessment.company_id].insert(0, assessment.assessment_id)

            self._persist()
            logger.info(f"Logged assessment {assessment.assessment_id}")
        except Exception as e:
            logger.error(f"Failed to log assessment: {e}")
            system_errors.labels(component="mcp_server").inc()

    async def get_assessment_history(self, company_id: str, limit: int = 10) -> List[Dict]:
        """Retrieve latest assessment history for a company"""
        try:
            ids = self.company_map.get(company_id, [])[:limit]
            return [self.assessments[aid] for aid in ids if aid in self.assessments]
        except Exception as e:
            logger.error(f"Failed to retrieve assessment history: {e}")
            system_errors.labels(component="mcp_server").inc()
            return []

    def get_system_metrics(self):
        """Return system metrics without Redis"""
        try:
            total_assessments = len(self.assessments)
            active_companies = len(self.company_map)
            return {
                "total_assessments": total_assessments,
                "active_companies": active_companies,
                "system_health": "healthy" if total_assessments >= 0 else "degraded",
                "timestamp": datetime.utcnow().isoformat(),
            }
        except Exception as e:
            logger.error(f"Failed to get system metrics: {e}")
            system_errors.labels(component="mcp_server").inc()
            return {
                "total_assessments": 0,
                "active_companies": 0,
                "system_health": "degraded",
                "timestamp": datetime.utcnow().isoformat(),
            }
