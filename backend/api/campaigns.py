"""
Campaign management endpoints
"""
from fastapi import APIRouter, HTTPException, Query
import json
from typing import Optional

from models import CampaignsResponse, CampaignSummary, CampaignDetail, ReportDetail, EntityCount
from database import execute_query
from utils.privacy import mask_entity

router = APIRouter()

@router.get("/campaigns", response_model=CampaignsResponse)
async def get_campaigns(
    status: str = Query("active", regex="^(active|resolved|all)$"),
    limit: int = Query(20, ge=1, le=100)
):
    """
    Get list of campaigns
    """
    if status == "all":
        query = """
            SELECT id, name, severity, report_count, first_seen, last_seen,
                   primary_technique, keywords, channels
            FROM campaigns
            ORDER BY last_seen DESC
            LIMIT ?
        """
        params = (limit,)
    else:
        query = """
            SELECT id, name, severity, report_count, first_seen, last_seen,
                   primary_technique, keywords, channels
            FROM campaigns
            WHERE status = ?
            ORDER BY last_seen DESC
            LIMIT ?
        """
        params = (status, limit)
    
    results = execute_query(query, params, fetch=True)
    
    campaigns = []
    for row in results:
        campaigns.append(CampaignSummary(
            id=row['id'],
            name=row['name'],
            severity=row['severity'],
            report_count=row['report_count'],
            first_seen=row['first_seen'],
            last_seen=row['last_seen'],
            primary_technique=row['primary_technique'],
            keywords=json.loads(row['keywords']) if row['keywords'] else [],
            channels=json.loads(row['channels']) if row['channels'] else []
        ))
    
    return CampaignsResponse(campaigns=campaigns)

@router.get("/campaigns/{campaign_id}", response_model=CampaignDetail)
async def get_campaign_detail(campaign_id: int):
    """
    Get detailed information about a specific campaign
    """
    # Get campaign info
    campaign_query = """
        SELECT id, name, severity, report_count
        FROM campaigns
        WHERE id = ?
    """
    
    campaign_result = execute_query(campaign_query, (campaign_id,), fetch=True)
    
    if not campaign_result:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    campaign = campaign_result[0]
    
    # Get sample reports (up to 10)
    reports_query = """
        SELECT message_text, timestamp, risk_score
        FROM reports
        WHERE campaign_id = ?
        ORDER BY timestamp DESC
        LIMIT 10
    """
    
    reports_result = execute_query(reports_query, (campaign_id,), fetch=True)
    
    sample_reports = [
        ReportDetail(
            message=r['message_text'][:200] + "..." if len(r['message_text']) > 200 else r['message_text'],
            timestamp=r['timestamp'],
            risk_score=r['risk_score']
        )
        for r in reports_result
    ]
    
    # Get top entities
    entities_query = """
        SELECT e.entity_type, e.entity_value, e.entity_hash, COUNT(*) as count
        FROM entities e
        JOIN reports r ON e.report_id = r.id
        WHERE r.campaign_id = ?
        GROUP BY e.entity_hash
        ORDER BY count DESC
        LIMIT 10
    """
    
    entities_result = execute_query(entities_query, (campaign_id,), fetch=True)
    
    top_entities = [
        EntityCount(
            type=e['entity_type'],
            value=mask_entity(e['entity_type'], e['entity_value']),
            count=e['count']
        )
        for e in entities_result
    ]
    
    return CampaignDetail(
        id=campaign['id'],
        name=campaign['name'],
        severity=campaign['severity'],
        report_count=campaign['report_count'],
        sample_reports=sample_reports,
        top_entities=top_entities
    )

@router.post("/campaigns/{campaign_id}/resolve")
async def resolve_campaign(campaign_id: int):
    """Mark a campaign as resolved"""
    result = execute_query(
        "UPDATE campaigns SET status = 'resolved' WHERE id = ?",
        (campaign_id,)
    )
    
    if result is None:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    return {"status": "success", "message": "Campaign marked as resolved"}
