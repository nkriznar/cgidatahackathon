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


class OporContext(BaseModel):
    """
    Optional OPOR (One Patient One Record) context from Layer 3.
    Allows KLARA to contextualize navigation decisions against
    a patient's existing health record (prior ED visits, active
    conditions, medications, etc.).
    """
    prior_ed_visits: Optional[int] = None
    active_conditions: Optional[List[str]] = None
    current_medications: Optional[List[str]] = None
    allergies: Optional[List[str]] = None
    last_visit_summary: Optional[str] = None


class ProvincialContext(BaseModel):
    """
    Provincial Context Analysis — data sourced from Layer 3
    (NS Health Capacity API, VirtualCareNS, EMR systems).
    Captures real-time or cached capacity and policy data
    used by the routing engine.
    """
    capacity_snapshot: Optional[dict] = None       # e.g. {"ed_wait": "3h", "utc_wait": "1h", ...}
    available_pathways: Optional[List[str]] = None  # resolved from region + policy
    policy_flags: Optional[List[str]] = None        # e.g. ["rural_override", "after_hours"]


class RoutingRecommendation(BaseModel):
    """
    Routing recommendation — pathway set aligned with Layer 4 care delivery nodes:
    ED, UTC, Primary Care, Pharmacy, Telehealth, Mental Health, Community Health Centres.

    Valid primary_pathway values:
      emergency, urgent, primarycare, pharmacy, virtualcarens,
      mental_health, community_health
    """
    primary_pathway: str
    reason: str
    options: List[str]


class SystemContext(BaseModel):
    region: str
    virtualcare_wait: str
    utc_wait: str
    pharmacy_available: bool


class StructuredSummary(BaseModel):
    """
    Structured Intake Output — the final output of the pipeline.
    Feeds Layer 1 (Clinician Intake Summary View) and
    Layer 3 (EMR integration).
    """
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
    opor_context: Optional[OporContext] = None  # Optional OPOR health record from Layer 3


class AssessResponse(BaseModel):
    session_id: str
    patient_input: PatientInput
    risk_assessment: RiskAssessment
    opor_context: Optional[OporContext] = None
    provincial_context: Optional[ProvincialContext] = None
    routing_recommendation: RoutingRecommendation
    system_context: SystemContext
    structured_summary: StructuredSummary
    governance: Governance
