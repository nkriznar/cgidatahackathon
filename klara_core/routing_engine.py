def route_care(risk_level: str, region: str) -> dict:
    """
    Capacity-Aware Routing Engine (Architecture Stage 5).

    Routes patients to the appropriate care delivery node (Layer 4)
    based on risk level and region.

    Data source: Parameters (wait times, capacity pressure) are sourced from
    the Healthcare System Integration Layer (Layer 3), specifically:
      - NS Health Capacity API  (real-time ED / UTC wait & occupancy)
      - VirtualCareNS availability
      - Regional EMR systems (Med Access, Accuro)

    Pathway set aligned with Layer 4 care delivery nodes:
      ED, UTC, Primary Care, Pharmacy, Telehealth,
      Mental Health, Community Health Centres.

    Note: Emergency cases are not routed by this model — they are handled
    by the Escalation Override Protocol (EMERGENCY node in the pipeline).
    """
    # Step 8.1 - Formulation: Use PuLP Optimization Model to route the patient
    from klara_core.optimization import optimize_pathways
    
    # Create a dummy "batch" of 1 representing the current session
    patients = [{"id": "current_patient", "risk": risk_level, "pref": "VirtualCareNS"}]
    
    # Layer 3 capacity overrides from API (simulated for prototype)
    # In production, this receives real-time occupancy. We set constraints loosely here for the demo.
    capacities = {"ED": 100, "UTC": 50, "VirtualCareNS": 200, "Pharmacy": 50, "Primary Care": 30, "Self-Care": 1000, "811": 500}
    
    opt_result = optimize_pathways(patients, capacities)
    assigned_pathway = opt_result["assignments"].get("current_patient", "811")
    solve_time = opt_result.get("solve_time_ms", 0.0)
    
    # Map the PuLP assignment back to the UI descriptions
    reason_map = {
        "ED": "Assigned via LP Model (Strain Minimization): High medical acuity requires immediate ED capacity.",
        "UTC": "Assigned via LP Model (Strain Minimization): Symptoms warrant assessment but divert from ED.",
        "VirtualCareNS": "Assigned via LP Model (Strain Minimization): High expected wait elsewhere; Virtual Care has capacity.",
        "Pharmacy": "Assigned via LP Model (Strain Minimization): Lowest system strain for this presentation.",
        "Primary Care": "Assigned via LP Model (Strain Minimization): Appropriate matched continuity of care.",
        "Self-Care": "Assigned via LP Model (Strain Minimization): Trivial severity, deflects system strain.",
        "811": "Assigned via LP Model (Strain Minimization): Tele-triage is the most efficient next step."
    }

    primary_pathway = assigned_pathway
    reason = f"{reason_map.get(assigned_pathway, 'Optimal pathway assigned.')} (Solved in {solve_time:.1f}ms)"
    
    # Provide fallback options for the dashboard
    options = [
        f"{assigned_pathway} in {region}",
        "811 Healthline",
        f"Community Health Centre in {region}"
    ]

    return {
        "primary_pathway": primary_pathway,
        "reason": reason,
        "options": options
    }
