def route_care(risk_level: str, region: str) -> dict:
    """
    Mock implementation returning a recommended pathway based on the risk level.
    """
    if risk_level == "high":
        primary_pathway = "Emergency Department"
        reason = "High risk symptoms require immediate in-person assessment."
        options = ["Call 911", f"Go to nearest ED in {region}"]
    elif risk_level == "moderate":
        primary_pathway = "Urgent Treatment Centre (UTC)"
        reason = "Symptoms warrant medical assessment but are not immediately life-threatening."
        options = [f"UTC in {region}", "VirtualCareNS"]
    else:  # low
        primary_pathway = "Pharmacy or Self-Care"
        reason = "Low risk symptoms can typically be managed via pharmacy consultation or self-care."
        options = [f"Local Pharmacy in {region}", "811 Healthline"]

    return {
        "primary_pathway": primary_pathway,
        "reason": reason,
        "options": options
    }
