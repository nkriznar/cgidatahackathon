def risk_score(symptoms: list) -> dict:
    """
    Mock implementation to return risk score, level, and emergency flags
    based on keyword detection.
    """
    score = 20
    level = "low"
    flags = []

    # Simple logic for mock functionality
    if "chest pain" in symptoms or "shortness of breath" in symptoms:
        score = 95
        level = "high"
        flags.append("Immediate emergency care recommended")
    elif "fever" in symptoms:
        score = 55
        level = "moderate"
    elif "headache" in symptoms or "pain" in symptoms:
        score = 30
        level = "low"
        
    return {
        "score": score,
        "level": level,
        "emergency_flags": flags
    }
