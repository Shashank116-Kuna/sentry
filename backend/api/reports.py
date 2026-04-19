"""
Report submission and processing endpoints
"""
from fastapi import APIRouter, Request, HTTPException
import json

from models import ReportRequest, ReportResponse
from database import execute_query
from security.rate_limiter import check_rate_limit
from security.validator import validate_message, validate_channel, sanitize_input
from utils.privacy import hash_ip, hash_value
from utils.scoring import calculate_risk_score, get_risk_level
from nlp.preprocessor import clean_text
from nlp.entity_extractor import extract_entities, count_entity_types
from nlp.technique_detector import detect_techniques
from nlp.campaign_clusterer import find_similar_campaign, create_campaign, update_campaign

router = APIRouter()

@router.post("/report", response_model=ReportResponse)
async def submit_report(report: ReportRequest, request: Request):
    """
    Submit a new scam report
    """
    # Rate limiting
    client_ip = request.client.host
    if not check_rate_limit(client_ip):
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Please try again later."
        )
    
    # Validate input
    is_valid, error = validate_message(report.message)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error)
    
    is_valid, error = validate_channel(report.channel)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error)
    
    # Sanitize input
    message = sanitize_input(report.message)
    channel = report.channel
    
    try:
        # NLP Processing Pipeline
        
        # 1. Extract entities
        entities = extract_entities(message)
        entity_counts = count_entity_types(entities)
        
        # 2. Detect techniques
        techniques = detect_techniques(message)
        
        # 3. Calculate risk score
        risk_score = calculate_risk_score(techniques, entity_counts)
        risk_level = get_risk_level(risk_score)
        
        # 4. Save report to database
        ip_hash = hash_ip(client_ip)
        
        query = """
            INSERT INTO reports (
                message_text, channel, reporter_ip_hash,
                risk_score, risk_level, techniques
            ) VALUES (?, ?, ?, ?, ?, ?)
        """
        
        report_id = execute_query(
            query,
            (message, channel, ip_hash, risk_score, risk_level, json.dumps(techniques))
        )
        
        # 5. Save entities
        for entity_type, values in entities.items():
            for value in values:
                entity_hash = hash_value(value)
                execute_query(
                    "INSERT INTO entities (report_id, entity_type, entity_value, entity_hash) VALUES (?, ?, ?, ?)",
                    (report_id, entity_type, value, entity_hash)
                )
        
        # 6. Campaign detection
        campaign_id = None
        
        if techniques:  # Only cluster if techniques detected
            campaign_id = find_similar_campaign(message, techniques, entities)
            
            if campaign_id:
                # Update existing campaign
                update_campaign(campaign_id, report_id, channel)
            else:
                # Check if this should start a new campaign (need more reports)
                # For now, create campaign immediately for demo purposes
                campaign_id = create_campaign(report_id, message, techniques, risk_level, channel)
        
        # 7. High-risk alert
        if risk_score >= 0.80:
            alert_msg = f"High-risk report detected: {techniques[:2]} (score: {risk_score})"
            execute_query(
                "INSERT INTO alerts (alert_type, message, severity) VALUES (?, ?, ?)",
                ('high_risk', alert_msg, 'High')
            )
        
        # Return response
        return ReportResponse(
            status="success",
            report_id=report_id,
            risk_level=risk_level,
            risk_score=risk_score,
            detected_techniques=techniques,
            campaign_id=campaign_id,
            message="Report submitted successfully"
        )
    
    except Exception as e:
        print(f"Error processing report: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/reports/{report_id}")
async def get_report(report_id: int):
    """Get details of a specific report"""
    query = """
        SELECT id, message_text, channel, timestamp, risk_score, risk_level,
               techniques, campaign_id
        FROM reports
        WHERE id = ?
    """
    
    result = execute_query(query, (report_id,), fetch=True)
    
    if not result:
        raise HTTPException(status_code=404, detail="Report not found")
    
    report = result[0]
    report['techniques'] = json.loads(report['techniques']) if report['techniques'] else []
    
    # Get entities
    entities_query = "SELECT entity_type, entity_value FROM entities WHERE report_id = ?"
    entities = execute_query(entities_query, (report_id,), fetch=True)
    report['entities'] = entities
    
    return report
