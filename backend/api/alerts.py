"""
Alerts and statistics endpoints
"""
from fastapi import APIRouter, Query
import json
from datetime import datetime, timedelta

from models import AlertsResponse, Alert, StatsResponse, ChannelStat, KeywordStat
from database import execute_query

router = APIRouter()

@router.get("/alerts", response_model=AlertsResponse)
async def get_alerts(limit: int = Query(20, ge=1, le=100)):
    """
    Get latest alerts
    """
    query = """
        SELECT id, alert_type, message, severity, campaign_id, created_at
        FROM alerts
        ORDER BY created_at DESC
        LIMIT ?
    """
    
    results = execute_query(query, (limit,), fetch=True)
    
    alerts = [
        Alert(
            id=row['id'],
            type=row['alert_type'],
            message=row['message'],
            severity=row['severity'],
            campaign_id=row['campaign_id'],
            created_at=row['created_at']
        )
        for row in results
    ]
    
    return AlertsResponse(alerts=alerts)

@router.get("/stats", response_model=StatsResponse)
async def get_stats():
    """
    Get dashboard statistics
    """
    # Total reports
    total_reports = execute_query(
        "SELECT COUNT(*) as count FROM reports",
        fetch=True
    )[0]['count']
    
    # Active campaigns
    active_campaigns = execute_query(
        "SELECT COUNT(*) as count FROM campaigns WHERE status = 'active'",
        fetch=True
    )[0]['count']
    
    # Reports in last 24 hours
    time_24h_ago = datetime.utcnow() - timedelta(hours=24)
    reports_24h = execute_query(
        "SELECT COUNT(*) as count FROM reports WHERE timestamp >= ?",
        (time_24h_ago,),
        fetch=True
    )[0]['count']
    
    # High risk reports
    high_risk_reports = execute_query(
        "SELECT COUNT(*) as count FROM reports WHERE risk_level = 'High'",
        fetch=True
    )[0]['count']
    
    # Top channels
    channel_stats = execute_query(
        """
        SELECT channel, COUNT(*) as count
        FROM reports
        GROUP BY channel
        ORDER BY count DESC
        LIMIT 5
        """,
        fetch=True
    )
    
    top_channels = [
        ChannelStat(channel=row['channel'], count=row['count'])
        for row in channel_stats
    ]
    
    # Trending keywords (from recent campaigns)
    keyword_stats = execute_query(
        """
        SELECT keywords
        FROM campaigns
        WHERE status = 'active'
        ORDER BY last_seen DESC
        LIMIT 10
        """,
        fetch=True
    )
    
    # Aggregate keywords
    keyword_counts = {}
    for row in keyword_stats:
        if row['keywords']:
            keywords = json.loads(row['keywords'])
            for kw in keywords:
                keyword_counts[kw] = keyword_counts.get(kw, 0) + 1
    
    # Sort and get top 10
    sorted_keywords = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    trending_keywords = [
        KeywordStat(keyword=kw, count=count)
        for kw, count in sorted_keywords
    ]
    
    return StatsResponse(
        total_reports=total_reports,
        active_campaigns=active_campaigns,
        reports_24h=reports_24h,
        high_risk_reports=high_risk_reports,
        top_channels=top_channels,
        trending_keywords=trending_keywords
    )
