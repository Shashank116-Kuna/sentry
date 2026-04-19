"""
IP-based rate limiting
"""
from datetime import datetime, timedelta
from database import execute_query
from config import RATE_LIMIT_REQUESTS, RATE_LIMIT_WINDOW
from utils.privacy import hash_ip

def check_rate_limit(ip: str) -> bool:
    """
    Check if IP is within rate limit
    Returns: True if allowed, False if rate limited
    """
    ip_hash = hash_ip(ip)
    
    # Get current rate limit entry
    result = execute_query(
        "SELECT request_count, window_start FROM rate_limit WHERE ip_hash = ?",
        (ip_hash,), fetch=True
    )
    
    current_time = datetime.utcnow()
    
    if not result:
        # First request from this IP
        execute_query(
            "INSERT INTO rate_limit (ip_hash, request_count, window_start) VALUES (?, 1, ?)",
            (ip_hash, current_time)
        )
        return True
    
    entry = result[0]
    window_start = datetime.fromisoformat(entry['window_start'])
    window_end = window_start + timedelta(seconds=RATE_LIMIT_WINDOW)
    
    if current_time > window_end:
        # Window expired, reset
        execute_query(
            "UPDATE rate_limit SET request_count = 1, window_start = ? WHERE ip_hash = ?",
            (current_time, ip_hash)
        )
        return True
    
    # Within window
    request_count = entry['request_count']
    
    if request_count >= RATE_LIMIT_REQUESTS:
        # Rate limited
        return False
    
    # Increment counter
    execute_query(
        "UPDATE rate_limit SET request_count = request_count + 1 WHERE ip_hash = ?",
        (ip_hash,)
    )
    return True

def cleanup_rate_limit():
    """Clean up expired rate limit entries (run periodically)"""
    cutoff = datetime.utcnow() - timedelta(seconds=RATE_LIMIT_WINDOW * 2)
    execute_query(
        "DELETE FROM rate_limit WHERE window_start < ?",
        (cutoff,)
    )
