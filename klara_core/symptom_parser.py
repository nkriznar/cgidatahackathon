def parse_symptoms(text: str) -> dict:
    """
    Mock implementation to extract a list of symptoms and duration from the input string.
    """
    text_lower = text.lower()
    symptoms = []
    
    # Mock keyword extraction
    if "headache" in text_lower:
        symptoms.append("headache")
    if "fever" in text_lower:
        symptoms.append("fever")
    if "pain" in text_lower:
        symptoms.append("pain")
    if "chest" in text_lower:
        symptoms.append("chest pain")
    if "breath" in text_lower or "shortness" in text_lower:
        symptoms.append("shortness of breath")

    if not symptoms:
        symptoms.append("unspecified symptom")

    # Mock duration extraction
    duration_hours = 24  # default mock duration
    
    return {
        "text": text,
        "symptoms": symptoms,
        "duration_hours": duration_hours
    }
