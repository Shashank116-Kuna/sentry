"""
Regex-based entity extraction for Indian context
"""
import re
from typing import List, Dict
from config import ENTITY_PATTERNS
from .preprocessor import normalize_phone, normalize_upi, normalize_url

def extract_entities(text: str) -> Dict[str, List[str]]:
    """
    Extract entities from text using regex patterns
    Returns: {entity_type: [entity_values]}
    """
    entities = {}
    
    # Extract phone numbers
    phones = re.findall(ENTITY_PATTERNS['phone'], text, re.IGNORECASE)
    if phones:
        entities['phone'] = [normalize_phone(p) for p in phones]
    
    # Extract UPI IDs
    upi_ids = re.findall(ENTITY_PATTERNS['upi'], text, re.IGNORECASE)
    if upi_ids:
        # Filter out common false positives (email-like patterns)
        valid_upis = [u for u in upi_ids if not re.search(r'@(gmail|yahoo|hotmail|outlook)', u, re.IGNORECASE)]
        if valid_upis:
            entities['upi_id'] = [normalize_upi(u) for u in valid_upis]
    
    # Extract URLs
    urls = re.findall(ENTITY_PATTERNS['url'], text, re.IGNORECASE)
    if urls:
        entities['url'] = [normalize_url(u) for u in urls]
    
    # Extract amounts
    amounts = re.findall(ENTITY_PATTERNS['amount'], text, re.IGNORECASE)
    if amounts:
        entities['amount'] = amounts
    
    # Extract PAN
    pans = re.findall(ENTITY_PATTERNS['pan'], text)
    if pans:
        entities['pan'] = pans
    
    # Extract Aadhaar
    aadhaars = re.findall(ENTITY_PATTERNS['aadhaar'], text)
    if aadhaars:
        entities['aadhaar'] = aadhaars
    
    # Extract bank names (common Indian banks)
    bank_pattern = r'\b(SBI|HDFC|ICICI|Axis|PNB|Bank of Baroda|Canara|Union Bank|BOI|BOB|Kotak|IDFC|Yes Bank|IndusInd)\b'
    banks = re.findall(bank_pattern, text, re.IGNORECASE)
    if banks:
        entities['bank_name'] = list(set(banks))
    
    return entities

def count_entity_types(entities: Dict[str, List[str]]) -> Dict[str, int]:
    """Count number of entities by type"""
    return {entity_type: len(values) for entity_type, values in entities.items()}
