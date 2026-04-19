"""
Text preprocessing for NLP pipeline
"""
import re
import unicodedata

def clean_text(text: str) -> str:
    """Clean and normalize text"""
    # Normalize unicode
    text = unicodedata.normalize('NFKD', text)
    
    # Convert to lowercase for analysis (keep original for display)
    text_lower = text.lower()
    
    # Remove excessive whitespace
    text_lower = re.sub(r'\s+', ' ', text_lower).strip()
    
    return text_lower

def extract_keywords(text: str, min_length: int = 3) -> list:
    """Extract meaningful keywords from text"""
    text_clean = clean_text(text)
    
    # Remove common stop words (basic set)
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were', 'be', 'been',
        'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'should',
        'can', 'could', 'may', 'might', 'must', 'your', 'you', 'this', 'that',
        'these', 'those', 'it', 'its', 'as', 'so', 'if', 'than', 'dear', 'sir',
        'madam', 'customer', 'please', 'kindly'
    }
    
    # Tokenize
    words = re.findall(r'\b\w+\b', text_clean)
    
    # Filter keywords
    keywords = [
        word for word in words 
        if len(word) >= min_length and word not in stop_words
    ]
    
    # Get unique keywords (case-insensitive)
    unique_keywords = list(dict.fromkeys(keywords))
    
    return unique_keywords[:20]  # Top 20 keywords

def normalize_phone(phone: str) -> str:
    """Normalize phone number format"""
    # Remove all non-digit characters
    digits = re.sub(r'\D', '', phone)
    
    # Remove country code if present
    if digits.startswith('91') and len(digits) == 12:
        digits = digits[2:]
    
    return digits

def normalize_upi(upi: str) -> str:
    """Normalize UPI ID"""
    return upi.lower().strip()

def normalize_url(url: str) -> str:
    """Normalize URL"""
    # Remove protocol
    url = re.sub(r'^https?://', '', url)
    # Remove trailing slash
    url = url.rstrip('/')
    return url.lower()
