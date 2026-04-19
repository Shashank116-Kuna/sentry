"""
Input validation and sanitization
"""
import re
from typing import Tuple

def validate_message(message: str) -> Tuple[bool, str]:
    """
    Validate report message
    Returns: (is_valid, error_message)
    """
    if not message or not message.strip():
        return False, "Message cannot be empty"
    
    if len(message) < 10:
        return False, "Message too short (minimum 10 characters)"
    
    if len(message) > 5000:
        return False, "Message too long (maximum 5000 characters)"
    
    # Check for spam patterns (repeated characters)
    if re.search(r'(.)\1{20,}', message):
        return False, "Message contains excessive repeated characters"
    
    # Check for obvious test/spam
    spam_patterns = [
        r'^(test|spam|xxx|zzz)+$',
        r'^[0-9]+$',  # Only numbers
        r'^[^a-zA-Z0-9\u0900-\u097F]+$'  # No alphanumeric or Hindi chars
    ]
    
    for pattern in spam_patterns:
        if re.match(pattern, message.strip(), re.IGNORECASE):
            return False, "Message appears to be spam or test data"
    
    return True, ""

def validate_channel(channel: str) -> Tuple[bool, str]:
    """Validate channel type"""
    from config import VALID_CHANNELS
    
    if channel not in VALID_CHANNELS:
        return False, f"Invalid channel. Must be one of: {', '.join(VALID_CHANNELS)}"
    
    return True, ""

def sanitize_input(text: str) -> str:
    """Sanitize user input"""
    # Remove null bytes
    text = text.replace('\x00', '')
    
    # Limit consecutive newlines
    text = re.sub(r'\n{4,}', '\n\n\n', text)
    
    # Trim whitespace
    text = text.strip()
    
    return text
