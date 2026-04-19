"""
Risk scoring and level assignment
"""
from typing import List, Dict
from config import TECHNIQUE_WEIGHTS, RISK_THRESHOLDS

def calculate_risk_score(techniques: List[str], entity_counts: Dict[str, int]) -> float:
    """
    Calculate risk score based on detected techniques and entities
    Formula: weighted_techniques + entity_multiplier
    """
    # Base score from techniques
    technique_score = sum(TECHNIQUE_WEIGHTS.get(tech, 0.1) for tech in techniques)
    
    # Entity multiplier (more entities = higher risk)
    entity_multiplier = 0.0
    if entity_counts.get('phone', 0) > 0:
        entity_multiplier += 0.10
    if entity_counts.get('upi_id', 0) > 0:
        entity_multiplier += 0.10
    if entity_counts.get('url', 0) > 0:
        entity_multiplier += 0.08
    if entity_counts.get('amount', 0) > 0:
        entity_multiplier += 0.05
    
    # Multiple techniques multiplier
    if len(techniques) >= 3:
        technique_score *= 1.2
    elif len(techniques) >= 2:
        technique_score *= 1.1
    
    total_score = min(technique_score + entity_multiplier, 1.0)
    return round(total_score, 2)

def get_risk_level(score: float) -> str:
    """Assign risk level based on score"""
    if score >= RISK_THRESHOLDS["high"]:
        return "High"
    elif score >= RISK_THRESHOLDS["medium"]:
        return "Medium"
    else:
        return "Low"

def get_severity_from_techniques(techniques: List[str]) -> str:
    """Determine campaign severity from common techniques"""
    high_risk_techniques = {"otp_harvesting", "upi_pin_request", "impersonation"}
    
    if any(tech in high_risk_techniques for tech in techniques):
        return "High"
    elif len(techniques) >= 2:
        return "Medium"
    else:
        return "Low"
