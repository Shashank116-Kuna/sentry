"""
Privacy utilities for hashing and masking sensitive data
"""
import hashlib
from config import HASH_SALT, PHONE_MASK_DIGITS

def hash_value(value: str) -> str:
    """Hash a value with salt for privacy"""
    salted = f"{value}{HASH_SALT}"
    return hashlib.sha256(salted.encode()).hexdigest()

def hash_ip(ip: str) -> str:
    """Hash IP address for rate limiting"""
    return hash_value(ip)

def mask_phone(phone: str) -> str:
    """Mask phone number (show first digits, hide last 5)"""
    if len(phone) <= PHONE_MASK_DIGITS:
        return "*" * len(phone)
    visible = len(phone) - PHONE_MASK_DIGITS
    return phone[:visible] + "*" * PHONE_MASK_DIGITS

def mask_entity(entity_type: str, entity_value: str) -> str:
    """Mask entity based on type"""
    if entity_type == "phone":
        return mask_phone(entity_value)
    elif entity_type == "upi_id":
        parts = entity_value.split("@")
        if len(parts) == 2:
            username = parts[0]
            if len(username) > 3:
                return username[:3] + "***@" + parts[1]
        return entity_value[:3] + "***"
    elif entity_type == "url":
        # Mask middle part of URL
        if len(entity_value) > 15:
            return entity_value[:10] + "***" + entity_value[-5:]
        return entity_value[:5] + "***"
    elif entity_type in ["pan", "aadhaar"]:
        # Mask all but first 2 chars
        if len(entity_value) > 2:
            return entity_value[:2] + "*" * (len(entity_value) - 2)
        return "**"
    else:
        return entity_value
