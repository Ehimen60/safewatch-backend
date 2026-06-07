from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class WorkerDetection(BaseModel):
    id: str
    status: str  # COMPLIANT, VIOLATION, WARNING
    present: List[str]
    missing: List[str]
    note: str

class ComplianceSummary(BaseModel):
    total_workers: int
    compliant: int
    violations: int
    warnings: int = 0
    compliance_rate: float
    site_status: str
    critical_findings: str
    recommendations: str

class AnalysisRequest(BaseModel):
    site_name: str = "Unnamed Site"
    ppe_requirements: List[str] = [
        "Safety Helmet",
        "High-Vis Vest",
        "Safety Gloves",
        "Face Mask",
        "Safety Boots"
    ]

class AnalysisResponse(BaseModel):
    report_id: str
    site_name: str
    timestamp: str
    filename: str
    workers: List[Dict[str, Any]]
    summary: Dict[str, Any]
    pdf_available: bool

class ReportSummary(BaseModel):
    id: str
    site_name: str
    filename: str
    timestamp: str
    total_workers: int
    compliance_rate: float
    site_status: str
