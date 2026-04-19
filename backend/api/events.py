"""
Server-Sent Events for real-time updates
"""
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import asyncio
import json
from datetime import datetime

from database import execute_query

router = APIRouter()

# Store last seen IDs to track new entries
last_alert_id = 0
last_report_id = 0

async def event_generator():
    """Generate SSE events for real-time updates"""
    global last_alert_id, last_report_id
    
    # Initialize with current max IDs
    alert_result = execute_query("SELECT MAX(id) as max_id FROM alerts", fetch=True)
    last_alert_id = alert_result[0]['max_id'] or 0
    
    report_result = execute_query("SELECT MAX(id) as max_id FROM reports", fetch=True)
    last_report_id = report_result[0]['max_id'] or 0
    
    while True:
        try:
            # Check for new alerts
            new_alerts = execute_query(
                """
                SELECT id, alert_type, message, severity, created_at
                FROM alerts
                WHERE id > ?
                ORDER BY id ASC
                """,
                (last_alert_id,),
                fetch=True
            )
            
            if new_alerts:
                for alert in new_alerts:
                    event_data = {
                        "type": "alert",
                        "data": {
                            "id": alert['id'],
                            "alert_type": alert['alert_type'],
                            "message": alert['message'],
                            "severity": alert['severity'],
                            "created_at": alert['created_at']
                        }
                    }
                    yield f"data: {json.dumps(event_data)}\n\n"
                    last_alert_id = alert['id']
            
            # Check for new reports
            new_reports = execute_query(
                """
                SELECT id, risk_level, techniques, timestamp
                FROM reports
                WHERE id > ?
                ORDER BY id ASC
                """,
                (last_report_id,),
                fetch=True
            )
            
            if new_reports:
                for report in new_reports:
                    event_data = {
                        "type": "report",
                        "data": {
                            "id": report['id'],
                            "risk_level": report['risk_level'],
                            "techniques": json.loads(report['techniques']) if report['techniques'] else [],
                            "timestamp": report['timestamp']
                        }
                    }
                    yield f"data: {json.dumps(event_data)}\n\n"
                    last_report_id = report['id']
            
            # Heartbeat to keep connection alive
            yield f": heartbeat\n\n"
            
            await asyncio.sleep(2)  # Check every 2 seconds
            
        except Exception as e:
            print(f"SSE error: {e}")
            break

@router.get("/events")
async def sse_events():
    """
    Server-Sent Events endpoint for real-time updates
    """
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
