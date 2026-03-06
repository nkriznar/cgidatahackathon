"""
KLARA OS Core Engine — /assess endpoint.

Pipeline mapping to the 7-stage architecture:
  Stage 1  Patient Input          → AssessRequest (Layer 1 → Layer 2)
  Stage 2  Symptom Parsing        → parse_symptoms()        [INTAKE]
  Stage 3  Risk Classification    → risk_score()             [RISK_ASSESS]
  Stage 4  Provincial Context     → load_provincial_context() [PROVINCIAL_CONTEXT]
  Stage 5  Capacity-Aware Routing → route_care()             [ROUTING_OPT]
  Stage 6  Care Recommendation    → build_summary()          [RESPONSE_GEN]
  Stage 7  Structured Intake Out  → AssessResponse           (Layer 2 → Layer 1 + Layer 3)

RESPONSE_GEN output is the official "Structured Intake Output" that feeds
Layer 1 (Clinician Intake Summary View) and Layer 3 (EMR integration).
"""

import uuid
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from klara_data.schemas import (
    AssessRequest,
    AssessResponse,
    PatientInput,
    RiskAssessment,
    OporContext,
    ProvincialContext,
    RoutingRecommendation,
    SystemContext,
    StructuredSummary,
    Governance,
)
from klara_core.symptom_parser import parse_symptoms
from klara_core.risk_engine import risk_score
from klara_core.provincial_context import load_provincial_context
from klara_core.routing_engine import route_care
from klara_core.summary_builder import build_summary

STATIC_DIR = Path(__file__).parent / "static"

app = FastAPI(title="KLARA OS Core Engine")

# ── Serve static assets (CSS, JS) ──
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/")
def root():
    """Serve the patient-facing user view."""
    return FileResponse(str(STATIC_DIR / "index.html"))


@app.get("/admin")
def admin():
    """Serve the clinician / admin dashboard."""
    return FileResponse(str(STATIC_DIR / "admin.html"))

@app.post("/assess", response_model=AssessResponse)
def assess_patient(request: AssessRequest):
    # ── Stage 2: Symptom Parsing (INTAKE = Patient Input + Symptom Parsing) ──
    parsed = parse_symptoms(request.text)

    # ── Stage 3: Risk Classification (RISK_ASSESS) ──
    risk_output = risk_score(parsed["symptoms"])

    # ── Stage 4: Provincial Context Analysis ──────────────────────────
    #  Loads capacity, available pathways, and policy flags from Layer 3
    #  (NS Health Capacity API, VirtualCareNS, EMR systems).
    #  Equivalent to: ELIGIBILITY + RAG_RETRIEVE + Layer 3 data.
    prov_ctx = load_provincial_context(request.region, risk_output["level"])

    # ── Stage 5: Capacity-Aware Routing (ROUTING_OPT) ──
    routing_output = route_care(risk_output["level"], request.region)

    # ── Stage 6: Care Recommendation / RESPONSE_GEN ──
    summary_output = build_summary(
        parsed["symptoms"],
        parsed["duration_hours"],
        risk_output["level"],
        routing_output["primary_pathway"]
    )

    # ── Stage 7: Structured Intake Output ─────────────────────────────
    #  This response is the official "Structured Intake Output" feeding:
    #   • Layer 1 — Clinician Intake Summary View
    #   • Layer 3 — EMR integration (Med Access / Accuro)
    response = AssessResponse(
        session_id=str(uuid.uuid4()),
        patient_input=PatientInput(
            text=parsed["text"],
            symptoms=parsed["symptoms"],
            duration_hours=parsed["duration_hours"]
        ),
        risk_assessment=RiskAssessment(
            score=risk_output["score"],
            level=risk_output["level"],
            emergency_flags=risk_output["emergency_flags"]
        ),
        opor_context=request.opor_context,  # pass through any OPOR data from Layer 3
        provincial_context=ProvincialContext(
            capacity_snapshot=prov_ctx["capacity_snapshot"],
            available_pathways=prov_ctx["available_pathways"],
            policy_flags=prov_ctx["policy_flags"],
        ),
        routing_recommendation=RoutingRecommendation(
            primary_pathway=routing_output["primary_pathway"],
            reason=routing_output["reason"],
            options=routing_output["options"]
        ),
        system_context=SystemContext(
            region=request.region,
            virtualcare_wait=prov_ctx["capacity_snapshot"].get("virtualcarens_wait", "unknown"),
            utc_wait=prov_ctx["capacity_snapshot"].get("utc_wait", "unknown"),
            pharmacy_available=prov_ctx["capacity_snapshot"].get("pharmacy_available", False)
        ),
        structured_summary=StructuredSummary(
            symptoms=summary_output["symptoms"],
            duration=summary_output["duration"],
            risk=summary_output["risk"],
            recommended_pathway=summary_output["recommended_pathway"]
        ),
        governance=Governance(
            confidence_score=0.92,
            audit_events=[
                "Stage 2 — Symptom text parsed (Symptom Parsing).",
                "Stage 3 — Risk assessed (Risk Classification).",
                "Stage 4 — Provincial context loaded from Layer 3.",
                "Stage 5 — Capacity-aware routing completed.",
                "Stage 6 — Care recommendation generated.",
                "Stage 7 — Structured Intake Output assembled.",
            ]
        )
    )

    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
