"""
Campaign detection using TF-IDF and cosine similarity
"""
import re
import math
from collections import Counter
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from database import execute_query
from config import SIMILARITY_THRESHOLD, CAMPAIGN_TIME_WINDOW, MIN_REPORTS_FOR_CAMPAIGN
from .preprocessor import clean_text, extract_keywords

def compute_tfidf(documents: List[str]) -> List[Dict[str, float]]:
    """
    Compute TF-IDF vectors for documents
    Returns: List of {word: tfidf_score} dicts
    """
    if not documents:
        return []
    
    # Compute term frequencies
    doc_term_freqs = []
    for doc in documents:
        words = clean_text(doc).split()
        word_counts = Counter(words)
        total_words = len(words)
        tf = {word: count / total_words for word, count in word_counts.items()}
        doc_term_freqs.append(tf)
    
    # Compute document frequencies
    all_words = set()
    for tf in doc_term_freqs:
        all_words.update(tf.keys())
    
    doc_freq = {}
    for word in all_words:
        doc_freq[word] = sum(1 for tf in doc_term_freqs if word in tf)
    
    # Compute IDF
    num_docs = len(documents)
    idf = {word: math.log(num_docs / df) for word, df in doc_freq.items()}
    
    # Compute TF-IDF
    tfidf_vectors = []
    for tf in doc_term_freqs:
        tfidf = {word: tf_score * idf[word] for word, tf_score in tf.items()}
        tfidf_vectors.append(tfidf)
    
    return tfidf_vectors

def cosine_similarity(vec1: Dict[str, float], vec2: Dict[str, float]) -> float:
    """Compute cosine similarity between two TF-IDF vectors"""
    if not vec1 or not vec2:
        return 0.0
    
    # Get common words
    common_words = set(vec1.keys()) & set(vec2.keys())
    
    if not common_words:
        return 0.0
    
    # Compute dot product
    dot_product = sum(vec1[word] * vec2[word] for word in common_words)
    
    # Compute magnitudes
    mag1 = math.sqrt(sum(score ** 2 for score in vec1.values()))
    mag2 = math.sqrt(sum(score ** 2 for score in vec2.values()))
    
    if mag1 == 0 or mag2 == 0:
        return 0.0
    
    return dot_product / (mag1 * mag2)

def find_similar_campaign(
    message: str,
    techniques: List[str],
    entities: Dict[str, List[str]]
) -> Optional[int]:
    """
    Find existing campaign that matches the new report
    Returns: campaign_id if match found, None otherwise
    """
    # Get recent active campaigns (within time window)
    time_threshold = datetime.utcnow() - timedelta(seconds=CAMPAIGN_TIME_WINDOW)
    
    query = """
        SELECT c.id, c.sample_message, c.primary_technique, r.message_text
        FROM campaigns c
        LEFT JOIN reports r ON r.campaign_id = c.id
        WHERE c.status = 'active' AND c.last_seen >= ?
    """
    
    results = execute_query(query, (time_threshold,), fetch=True)
    
    if not results:
        return None
    
    # Group messages by campaign
    campaigns = {}
    for row in results:
        cid = row['id']
        if cid not in campaigns:
            campaigns[cid] = {
                'id': cid,
                'messages': [],
                'primary_technique': row['primary_technique']
            }
        if row['message_text']:
            campaigns[cid]['messages'].append(row['message_text'])
    
    # Check similarity with each campaign
    new_message_clean = clean_text(message)
    
    for cid, campaign_data in campaigns.items():
        campaign_messages = campaign_data['messages']
        
        if not campaign_messages:
            continue
        
        # Check technique overlap
        if campaign_data['primary_technique'] in techniques:
            # Compute TF-IDF similarity
            all_messages = campaign_messages + [message]
            tfidf_vectors = compute_tfidf(all_messages)
            
            if not tfidf_vectors:
                continue
            
            new_vec = tfidf_vectors[-1]
            
            # Check similarity with any message in campaign
            for i, old_vec in enumerate(tfidf_vectors[:-1]):
                similarity = cosine_similarity(new_vec, old_vec)
                
                if similarity >= SIMILARITY_THRESHOLD:
                    return cid
        
        # Check entity overlap (strong signal)
        if entities:
            # Check if any phone/UPI matches
            campaign_query = """
                SELECT entity_type, entity_hash
                FROM entities
                WHERE report_id IN (
                    SELECT id FROM reports WHERE campaign_id = ?
                )
            """
            campaign_entities = execute_query(campaign_query, (cid,), fetch=True)
            
            # Simple overlap check (can be enhanced)
            if campaign_entities and len(campaign_entities) >= 2:
                # If multiple entities match, likely same campaign
                return cid
    
    return None

def create_campaign(
    report_id: int,
    message: str,
    techniques: List[str],
    risk_level: str,
    channel: str
) -> int:
    """Create a new campaign"""
    keywords = extract_keywords(message)
    primary_technique = techniques[0] if techniques else "unknown"
    
    # Generate campaign name
    if 'otp_harvesting' in techniques or 'personal_info' in techniques:
        name = "KYC/OTP Phishing Campaign"
    elif 'upi_pin_request' in techniques:
        name = "UPI PIN Harvesting Campaign"
    elif 'authority' in techniques and 'fear' in techniques:
        name = "Authority Impersonation Scam"
    elif 'money_transfer' in techniques:
        name = "Fake Refund/Prize Scam"
    else:
        name = f"{primary_technique.replace('_', ' ').title()} Campaign"
    
    query = """
        INSERT INTO campaigns (
            name, first_seen, last_seen, report_count, severity,
            primary_technique, sample_message, keywords, channels
        ) VALUES (?, datetime('now'), datetime('now'), 1, ?, ?, ?, ?, ?)
    """
    
    import json
    campaign_id = execute_query(
        query,
        (name, risk_level, primary_technique, message[:500], 
         json.dumps(keywords), json.dumps([channel]))
    )
    
    # Update report with campaign_id
    execute_query(
        "UPDATE reports SET campaign_id = ? WHERE id = ?",
        (campaign_id, report_id)
    )
    
    return campaign_id

def update_campaign(campaign_id: int, report_id: int, channel: str):
    """Update existing campaign with new report"""
    import json
    
    # Get current campaign data
    campaign = execute_query(
        "SELECT keywords, channels FROM campaigns WHERE id = ?",
        (campaign_id,), fetch=True
    )[0]
    
    # Update campaign
    query = """
        UPDATE campaigns
        SET last_seen = datetime('now'),
            report_count = report_count + 1
        WHERE id = ?
    """
    execute_query(query, (campaign_id,))
    
    # Update report
    execute_query(
        "UPDATE reports SET campaign_id = ? WHERE id = ?",
        (campaign_id, report_id)
    )
    
    # Update channels if new
    channels = json.loads(campaign['channels']) if campaign['channels'] else []
    if channel not in channels:
        channels.append(channel)
        execute_query(
            "UPDATE campaigns SET channels = ? WHERE id = ?",
            (json.dumps(channels), campaign_id)
        )
    
    # Check if campaign should trigger alert
    check_campaign_alerts(campaign_id)

def check_campaign_alerts(campaign_id: int):
    """Check if campaign should generate alerts"""
    from config import ALERT_SURGE_THRESHOLD
    
    # Get campaign data
    campaign = execute_query(
        "SELECT report_count, name, severity FROM campaigns WHERE id = ?",
        (campaign_id,), fetch=True
    )[0]
    
    # New campaign alert (at threshold)
    if campaign['report_count'] == MIN_REPORTS_FOR_CAMPAIGN:
        alert_msg = f"New campaign detected: {campaign['name']} ({campaign['report_count']} reports)"
        execute_query(
            "INSERT INTO alerts (alert_type, message, severity, campaign_id) VALUES (?, ?, ?, ?)",
            ('new_campaign', alert_msg, campaign['severity'], campaign_id)
        )
    
    # Surge alert (rapid increase)
    elif campaign['report_count'] > 0 and campaign['report_count'] % ALERT_SURGE_THRESHOLD == 0:
        alert_msg = f"Campaign surge: {campaign['name']} ({campaign['report_count']} reports)"
        execute_query(
            "INSERT INTO alerts (alert_type, message, severity, campaign_id) VALUES (?, ?, ?, ?)",
            ('surge', alert_msg, 'High', campaign_id)
        )
