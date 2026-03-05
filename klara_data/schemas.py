from pydantic import BaseModel, Field
from typing import List, Optional

class PatientInput(BaseModel):
    text: str
    symptoms: List[str]
    duration_hours: int

class RiskAssessment(BaseModel):
    score: int = Field(ge=0, le=100)
    level: str  # e.g., 'low', 'moderate', 'high'
    emergency_flags: List[str]

class RoutingRecommendation(BaseModel):
    primary_pathway: str
    reason: str
    options: List[str]

class SystemContext(BaseModel):
    region: str
    virtualcare_wait: str
    utc_wait: str
    pharmacy_available: bool

class StructuredSummary(BaseModel):
    symptoms: str
    duration: str
    risk: str
    recommended_pathway: str

class Governance(BaseModel):
    confidence_score: float
    audit_events: List[str]

class AssessRequest(BaseModel):
    text: str
    region: str

class AssessResponse(BaseModel):
    session_id: str
    patient_input: PatientInput
    risk_assessment: RiskAssessment
    routing_recommendation: RoutingRecommendation
    system_context: SystemContext
    structured_summary: StructuredSummary
    governance: Governance
