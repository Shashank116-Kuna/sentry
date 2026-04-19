"""
Pydantic models for request/response validation
"""
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import datetime
from config import VALID_CHANNELS

class ReportRequest(BaseModel):
    message: str = Field(..., min_length=10, max_length=5000)
    channel: str = Field(..., pattern=f"^({'|'.join(VALID_CHANNELS)})$")
    
    @field_validator('message')
    @classmethod
    def validate_message(cls, v):
        if not v.strip():
            raise ValueError("Message cannot be empty")
        return v.strip()

class ReportResponse(BaseModel):
    status: str
    report_id: int
    risk_level: str
    risk_score: float
    detected_techniques: List[str]
    campaign_id: Optional[int] = None
    message: Optional[str] = None

class Alert(BaseModel):
    id: int
    type: str
    message: str
    severity: str
    campaign_id: Optional[int] = None
    created_at: datetime

class AlertsResponse(BaseModel):
    alerts: List[Alert]

class CampaignSummary(BaseModel):
    id: int
    name: str
    severity: str
    report_count: int
    first_seen: datetime
    last_seen: datetime
    primary_technique: str
    keywords: List[str]
    channels: List[str]

class CampaignsResponse(BaseModel):
    campaigns: List[CampaignSummary]

class ReportDetail(BaseModel):
    message: str
    timestamp: datetime
    risk_score: float

class EntityCount(BaseModel):
    type: str
    value: str
    count: int

class CampaignDetail(BaseModel):
    id: int
    name: str
    severity: str
    report_count: int
    sample_reports: List[ReportDetail]
    top_entities: List[EntityCount]

class ChannelStat(BaseModel):
    channel: str
    count: int

class KeywordStat(BaseModel):
    keyword: str
    count: int

class StatsResponse(BaseModel):
    total_reports: int
    active_campaigns: int
    reports_24h: int
    high_risk_reports: int
    top_channels: List[ChannelStat]
    trending_keywords: List[KeywordStat]
