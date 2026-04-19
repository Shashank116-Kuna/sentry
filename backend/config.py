"""
SENTRY Configuration
"""
import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent.parent

# Database
DATABASE_PATH = BASE_DIR / "data" / "sentry.db"

# Security
SECRET_KEY = os.getenv("SECRET_KEY", "sentry-dev-key-change-in-production")
RATE_LIMIT_REQUESTS = 10  # requests per window
RATE_LIMIT_WINDOW = 300  # 5 minutes in seconds

# NLP & Detection
SIMILARITY_THRESHOLD = 0.65  # Cosine similarity for campaign clustering
CAMPAIGN_TIME_WINDOW = 24 * 60 * 60  # 24 hours in seconds
MIN_REPORTS_FOR_CAMPAIGN = 3

# Risk scoring weights
TECHNIQUE_WEIGHTS = {
    "authority": 0.20,
    "urgency": 0.15,
    "fear": 0.15,
    "impersonation": 0.20,
    "otp_harvesting": 0.25,
    "upi_pin_request": 0.25,
    "money_transfer": 0.18,
    "link_click": 0.12,
    "personal_info": 0.15
}

# Risk level thresholds
RISK_THRESHOLDS = {
    "high": 0.60,
    "medium": 0.35,
    "low": 0.0
}

# Entity patterns
ENTITY_PATTERNS = {
    "phone": r'\b(?:\+91[-\s]?)?[6-9]\d{9}\b',
    "upi": r'\b[\w\.-]+@[\w]+\b',
    "url": r'https?://[^\s]+|(?:bit\.ly|tinyurl\.com)/[\w]+',
    "amount": r'(?:Rs\.?|₹|INR)\s*[\d,]+(?:\.\d{2})?|\b\d{1,5}(?:,\d{3})*(?:\.\d{2})?\s*(?:rupees?|Rs\.?|₹)',
    "pan": r'\b[A-Z]{5}\d{4}[A-Z]\b',
    "aadhaar": r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}\b'
}

# Technique detection keywords (English + Hindi/Hinglish)
TECHNIQUE_KEYWORDS = {
    "authority": [
        r'\b(?:bank|rbi|income tax|it department|police|government|ministry|sebi|uidai|aadhaar|authority)\b',
        r'\b(?:sarkar|vibhag|adhikari|mantralaya)\b'
    ],
    "urgency": [
        r'\b(?:urgent|immediately|within|expire[ds]?|last chance|final notice|today|now|asap|hurry)\b',
        r'\b(?:turant|jaldi|abhi|aaj)\b'
    ],
    "fear": [
        r'\b(?:blocked?|suspend|deactivate|penalty|fine|arrest|legal action|court|FIR|criminal|frozen)\b',
        r'\b(?:band|rok|saza|karwai)\b'
    ],
    "impersonation": [
        r'\b(?:dear customer|valued customer|account holder|sir/madam|respected)\b',
        r'\b(?:customer care|support team|helpline|official)\b'
    ],
    "otp_harvesting": [
        r'\b(?:OTP|one[- ]time password|verification code|PIN|CVV|security code|confirm|verify)\b',
        r'\b(?:share|provide|send|enter|submit|update).{0,30}(?:OTP|pin|code)\b'
    ],
    "upi_pin_request": [
        r'\b(?:UPI PIN|mPIN|ATM PIN|debit card pin)\b',
        r'\b(?:enter|share|update|verify).{0,20}(?:pin|UPI)\b'
    ],
    "money_transfer": [
        r'\b(?:send money|transfer|payment|refund|cashback|credited|won prize|lottery)\b',
        r'\b(?:paisa|paise|bhejo|transfer karo|amount)\b'
    ],
    "link_click": [
        r'\b(?:click here|visit|download|install|update|link|tap)\b',
        r'\bclick\s+(?:on\s+)?(?:this|the|here|below)\b'
    ],
    "personal_info": [
        r'\b(?:PAN|Aadhaar|KYC|date of birth|DOB|mother name|account number|card number)\b',
        r'\b(?:update|verify|confirm|re-?KYC|e-?KYC)\b'
    ]
}

# Channel types
VALID_CHANNELS = ["SMS", "WhatsApp", "Call", "Email", "UPI", "Other"]

# Alert settings
ALERT_SURGE_THRESHOLD = 5
ALERT_HIGH_RISK_THRESHOLD = 0.80

# Privacy
PHONE_MASK_DIGITS = 5
HASH_SALT = os.getenv("HASH_SALT", "sentry-salt-2026")