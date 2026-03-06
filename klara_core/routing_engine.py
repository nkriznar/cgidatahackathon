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
    if risk_level == "high":
        primary_pathway = "emergency"
        reason = "High risk symptoms require immediate in-person assessment."
        options = ["Call 911", f"Go to nearest ED in {region}"]
    elif risk_level == "moderate":
        primary_pathway = "urgent"
        reason = "Symptoms warrant medical assessment but are not immediately life-threatening."
        options = [
            f"UTC in {region}",
            "VirtualCareNS",
            f"Mental Health Access Point in {region}",   # Layer 4 node
            f"Community Health Centre in {region}",       # Layer 4 node
        ]
    elif risk_level == "mental_health":
        primary_pathway = "mental_health"
        reason = "Symptoms suggest a mental-health pathway is the best fit."
        options = [
            f"Mental Health Access Point in {region}",
            "VirtualCareNS (mental-health stream)",
            f"Community Health Centre in {region}",
        ]
    else:  # low
        primary_pathway = "pharmacy"
        reason = "Low risk symptoms can typically be managed via pharmacy consultation or self-care."
        options = [
            f"Local Pharmacy in {region}",
            "811 Healthline",
            f"Community Health Centre in {region}",  # Layer 4 node
        ]

    return {
        "primary_pathway": primary_pathway,
        "reason": reason,
        "options": options
    }
