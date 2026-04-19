/**
 * SENTRY Dashboard JavaScript
 */

const API_BASE = 'http://localhost:8000/api';
let eventSource = null;

// Initialize dashboard
document.addEventListener('DOMContentLoaded', () => {
    loadStats();
    loadCampaigns();
    loadAlerts();
    setupReportForm();
    connectSSE();
    
    // Refresh data every 30 seconds
    setInterval(() => {
        loadStats();
        loadCampaigns();
        loadAlerts();
    }, 30000);
});

// Load statistics
async function loadStats() {
    try {
        const response = await fetch(`${API_BASE}/stats`);
        const data = await response.json();
        
        document.getElementById('totalReports').textContent = data.total_reports;
        document.getElementById('activeCampaigns').textContent = data.active_campaigns;
        document.getElementById('reports24h').textContent = data.reports_24h;
        document.getElementById('highRiskReports').textContent = data.high_risk_reports;
        
        // Trending keywords
        const keywordsDiv = document.getElementById('trendingKeywords');
        if (data.trending_keywords.length > 0) {
            keywordsDiv.innerHTML = data.trending_keywords
                .map(kw => `<span class="keyword-badge">${kw.keyword} (${kw.count})</span>`)
                .join('');
        } else {
            keywordsDiv.innerHTML = '<em class="text-muted">No trending keywords yet</em>';
        }
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

// Load campaigns
async function loadCampaigns() {
    try {
        const response = await fetch(`${API_BASE}/campaigns?limit=10`);
        const data = await response.json();
        
        const campaignsDiv = document.getElementById('campaignsList');
        
        if (data.campaigns.length === 0) {
            campaignsDiv.innerHTML = '<p class="text-muted">No active campaigns</p>';
            return;
        }
        
        campaignsDiv.innerHTML = data.campaigns.map(campaign => `
            <div class="card campaign-card" onclick="showCampaignDetails(${campaign.id})">
                <div class="card-body">
                    <div class="d-flex justify-content-between align-items-start">
                        <div>
                            <h6 class="mb-1">${campaign.name}</h6>
                            <small class="text-muted">
                                <i class="fas fa-chart-line"></i> ${campaign.report_count} reports
                            </small>
                        </div>
                        <span class="badge severity-${campaign.severity.toLowerCase()}">
                            ${campaign.severity}
                        </span>
                    </div>
                    <div class="mt-2">
                        <small class="text-muted">
                            <i class="fas fa-clock"></i> 
                            Last seen: ${formatTimestamp(campaign.last_seen)}
                        </small>
                    </div>
                    <div class="mt-2">
                        ${campaign.keywords.slice(0, 3).map(kw => 
                            `<span class="badge bg-light text-dark">${kw}</span>`
                        ).join(' ')}
                    </div>
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading campaigns:', error);
    }
}

// Load alerts
async function loadAlerts() {
    try {
        const response = await fetch(`${API_BASE}/alerts?limit=15`);
        const data = await response.json();
        
        const alertsDiv = document.getElementById('alertsList');
        
        if (data.alerts.length === 0) {
            alertsDiv.innerHTML = '<p class="text-muted">No alerts</p>';
            return;
        }
        
        alertsDiv.innerHTML = data.alerts.map(alert => `
            <div class="alert-item">
                <div class="d-flex justify-content-between">
                    <strong>${getAlertIcon(alert.type)} ${alert.message}</strong>
                    <span class="badge severity-${alert.severity.toLowerCase()}">${alert.severity}</span>
                </div>
                <small class="text-muted">
                    ${formatTimestamp(alert.created_at)}
                </small>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading alerts:', error);
    }
}

// Show campaign details in modal
async function showCampaignDetails(campaignId) {
    try {
        const response = await fetch(`${API_BASE}/campaigns/${campaignId}`);
        const campaign = await response.json();
        
        const detailsDiv = document.getElementById('campaignDetails');
        detailsDiv.innerHTML = `
            <h5>${campaign.name}</h5>
            <p><strong>Severity:</strong> <span class="badge severity-${campaign.severity.toLowerCase()}">${campaign.severity}</span></p>
            <p><strong>Total Reports:</strong> ${campaign.report_count}</p>
            
            <h6 class="mt-3">Sample Reports</h6>
            ${campaign.sample_reports.map(report => `
                <div class="card mb-2">
                    <div class="card-body">
                        <p class="mb-1">${report.message}</p>
                        <small class="text-muted">
                            Risk Score: ${report.risk_score} | ${formatTimestamp(report.timestamp)}
                        </small>
                    </div>
                </div>
            `).join('')}
            
            <h6 class="mt-3">Top Entities</h6>
            <table class="table table-sm">
                <thead>
                    <tr>
                        <th>Type</th>
                        <th>Value</th>
                        <th>Count</th>
                    </tr>
                </thead>
                <tbody>
                    ${campaign.top_entities.map(entity => `
                        <tr>
                            <td><span class="badge bg-secondary">${entity.type}</span></td>
                            <td><code>${entity.value}</code></td>
                            <td>${entity.count}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
        
        const modal = new bootstrap.Modal(document.getElementById('campaignModal'));
        modal.show();
    } catch (error) {
        console.error('Error loading campaign details:', error);
    }
}

// Setup report form submission
function setupReportForm() {
    const form = document.getElementById('reportForm');
    const resultDiv = document.getElementById('reportResult');
    
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const message = document.getElementById('messageInput').value;
        const channel = document.getElementById('channelInput').value;
        
        resultDiv.innerHTML = '<div class="alert alert-info">Submitting...</div>';
        
        try {
            const response = await fetch(`${API_BASE}/report`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ message, channel })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                resultDiv.innerHTML = `
                    <div class="alert alert-success">
                        <strong>Report submitted successfully!</strong><br>
                        Risk Level: <span class="badge severity-${data.risk_level.toLowerCase()}">${data.risk_level}</span><br>
                        Risk Score: ${data.risk_score}<br>
                        Techniques: ${data.detected_techniques.join(', ')}
                    </div>
                `;
                form.reset();
                
                // Reload data
                setTimeout(() => {
                    loadStats();
                    loadCampaigns();
                    loadAlerts();
                }, 1000);
            } else {
                resultDiv.innerHTML = `<div class="alert alert-danger">${data.detail}</div>`;
            }
        } catch (error) {
            resultDiv.innerHTML = '<div class="alert alert-danger">Error submitting report</div>';
            console.error('Error submitting report:', error);
        }
    });
}

// Connect to SSE for real-time updates
function connectSSE() {
    try {
        eventSource = new EventSource(`${API_BASE}/events`);
        
        eventSource.onmessage = (event) => {
            const data = JSON.parse(event.data);
            
            if (data.type === 'alert') {
                // Show notification
                showNotification('New Alert', data.data.message);
                loadAlerts();
            } else if (data.type === 'report') {
                loadStats();
            }
        };
        
        eventSource.onerror = () => {
            console.error('SSE connection error');
            eventSource.close();
            // Reconnect after 5 seconds
            setTimeout(connectSSE, 5000);
        };
    } catch (error) {
        console.error('Error connecting SSE:', error);
    }
}

// Helper functions
function formatTimestamp(timestamp) {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = Math.floor((now - date) / 1000); // seconds
    
    if (diff < 60) return 'Just now';
    if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
    if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
    return `${Math.floor(diff / 86400)}d ago`;
}

function getAlertIcon(type) {
    const icons = {
        'new_campaign': '<i class="fas fa-flag text-danger"></i>',
        'surge': '<i class="fas fa-exclamation-triangle text-warning"></i>',
        'high_risk': '<i class="fas fa-fire text-danger"></i>'
    };
    return icons[type] || '<i class="fas fa-bell"></i>';
}

function showNotification(title, message) {
    if ('Notification' in window && Notification.permission === 'granted') {
        new Notification(title, { body: message });
    }
}

// Request notification permission
if ('Notification' in window && Notification.permission === 'default') {
    Notification.requestPermission();
}
