"""
Rule-based social engineering technique detection
"""
import re
from typing import List, Set
from config import TECHNIQUE_KEYWORDS
from .preprocessor import clean_text

def detect_techniques(text: str) -> List[str]:
    """
    Detect social engineering techniques using keyword patterns
    Returns: List of detected technique names
    """
    text_clean = clean_text(text)
    detected: Set[str] = set()
    
    # Check each technique
    for technique, patterns in TECHNIQUE_KEYWORDS.items():
        for pattern in patterns:
            if re.search(pattern, text_clean, re.IGNORECASE):
                detected.add(technique)
                break  # Found one match for this technique, move to next
    
    # Additional composite rules
    
    # OTP + urgency/authority = high risk OTP harvesting
    if 'otp_harvesting' in detected and ('urgency' in detected or 'authority' in detected):
        detected.add('otp_harvesting')  # Reinforce
    
    # Money transfer + impersonation = likely scam
    if 'money_transfer' in detected and 'impersonation' in detected:
        detected.add('money_transfer')
    
    # Link + urgency/fear = phishing
    if 'link_click' in detected and ('urgency' in detected or 'fear' in detected):
        detected.add('link_click')
    
    return sorted(list(detected))

def explain_techniques(techniques: List[str]) -> dict:
    """Provide human-readable explanations for detected techniques"""
    explanations = {
        "authority": "Impersonating authority figures (bank, police, government)",
        "urgency": "Creating false time pressure",
        "fear": "Threatening account block, legal action, or penalties",
        "impersonation": "Pretending to be legitimate organization",
        "otp_harvesting": "Attempting to collect OTP or verification codes",
        "upi_pin_request": "Requesting UPI PIN or ATM PIN",
        "money_transfer": "Requesting money transfer or payment",
        "link_click": "Urging to click suspicious links",
        "personal_info": "Requesting sensitive personal information (PAN, Aadhaar, KYC)"
    }
    
    return {tech: explanations.get(tech, "Unknown technique") for tech in techniques}
