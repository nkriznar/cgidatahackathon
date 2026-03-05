import uuid
from fastapi import FastAPI
from klara_data.schemas import (
    AssessRequest,
    AssessResponse,
    PatientInput,
    RiskAssessment,
    RoutingRecommendation,
    SystemContext,
    StructuredSummary,
    Governance,
)
from klara_core.symptom_parser import parse_symptoms
from klara_core.risk_engine import risk_score
from klara_core.routing_engine import route_care
from klara_core.summary_builder import build_summary

app = FastAPI(title="KLARA OS Core Engine")

@app.post("/assess", response_model=AssessResponse)
def assess_patient(request: AssessRequest):
    # 1. Parsing
    parsed = parse_symptoms(request.text)
    
    # 2. Risk Assessment
    risk_output = risk_score(parsed["symptoms"])
    
    # 3. Routing
    routing_output = route_care(risk_output["level"], request.region)
    
    # 4. Final Summary Integration
    summary_output = build_summary(
        parsed["symptoms"],
        parsed["duration_hours"],
        risk_output["level"],
        routing_output["primary_pathway"]
    )
    
    # Constructing the master Pydantic response enforcing the JSON payload
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
        routing_recommendation=RoutingRecommendation(
            primary_pathway=routing_output["primary_pathway"],
            reason=routing_output["reason"],
            options=routing_output["options"]
        ),
        system_context=SystemContext(
            region=request.region,
            virtualcare_wait="2 hours",  # Mock system context values
            utc_wait="4 hours",
            pharmacy_available=True
        ),
        structured_summary=StructuredSummary(
            symptoms=summary_output["symptoms"],
            duration=summary_output["duration"],
            risk=summary_output["risk"],
            recommended_pathway=summary_output["recommended_pathway"]
        ),
        governance=Governance(
            confidence_score=0.92,       # Mock system values
            audit_events=[
                "Symptom text parsed.",
                "Risk assessed based on symptoms.",
                "Pathway recommendation generated."
            ]
        )
    )

    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
