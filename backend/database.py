"""
Database initialization and connection
"""
import sqlite3
from pathlib import Path
from contextlib import contextmanager
from config import DATABASE_PATH

def init_database():
    """Initialize database with schema"""
    DATABASE_PATH.parent.mkdir(exist_ok=True)
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Reports table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message_text TEXT NOT NULL,
            channel TEXT NOT NULL CHECK(channel IN ('SMS', 'WhatsApp', 'Call', 'Email', 'UPI', 'Other')),
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            reporter_ip_hash TEXT,
            risk_score REAL,
            risk_level TEXT CHECK(risk_level IN ('Low', 'Medium', 'High')),
            techniques TEXT,
            campaign_id INTEGER,
            FOREIGN KEY (campaign_id) REFERENCES campaigns(id)
        )
    """)
    
    # Entities table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS entities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            report_id INTEGER NOT NULL,
            entity_type TEXT NOT NULL CHECK(entity_type IN ('phone', 'upi_id', 'url', 'amount', 'bank_name', 'pan', 'aadhaar')),
            entity_value TEXT NOT NULL,
            entity_hash TEXT,
            FOREIGN KEY (report_id) REFERENCES reports(id)
        )
    """)
    
    # Campaigns table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS campaigns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            first_seen DATETIME,
            last_seen DATETIME,
            report_count INTEGER DEFAULT 1,
            severity TEXT CHECK(severity IN ('Low', 'Medium', 'High')),
            primary_technique TEXT,
            sample_message TEXT,
            keywords TEXT,
            channels TEXT,
            status TEXT DEFAULT 'active' CHECK(status IN ('active', 'resolved'))
        )
    """)
    
    # Alerts table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            alert_type TEXT NOT NULL CHECK(alert_type IN ('new_campaign', 'surge', 'high_risk')),
            message TEXT NOT NULL,
            severity TEXT CHECK(severity IN ('Low', 'Medium', 'High')),
            campaign_id INTEGER,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (campaign_id) REFERENCES campaigns(id)
        )
    """)
    
    # Rate limit table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rate_limit (
            ip_hash TEXT PRIMARY KEY,
            request_count INTEGER DEFAULT 1,
            window_start DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_reports_timestamp ON reports(timestamp)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_reports_campaign ON reports(campaign_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_entities_type ON entities(entity_type)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_entities_hash ON entities(entity_hash)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_campaigns_status ON campaigns(status)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_alerts_created ON alerts(created_at)")
    
    conn.commit()
    conn.close()
    print(f"✓ Database initialized at {DATABASE_PATH}")

@contextmanager
def get_db():
    """Context manager for database connections"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def execute_query(query, params=None, fetch=False):
    """Execute a query and optionally fetch results"""
    with get_db() as conn:
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        if fetch:
            return [dict(row) for row in cursor.fetchall()]
        else:
            conn.commit()
            return cursor.lastrowid
