# LBCA AI Monitoring System - Quick Start Guide

## Installation & Setup

### 1. Install Dependencies
```bash
cd "c:\Users\Dell\Desktop\DJANGO\AI - Model"
pip install -r requirements.txt
```

### 2. Run the Server
```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: `http://localhost:8000`

### 3. API Documentation (Auto-generated)
Once server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## Project Structure

```
DJANGO/AI - Model/
├── requirements.txt              # Dependencies
├── API_DOCUMENTATION.md          # Full API reference
├── QUICK_START.md               # This file
├── ARCHITECTURE.md              # System design (to create)
│
├── app/
│   ├── main.py                  # FastAPI app + all endpoints
│   ├── model.py                 # Model loading (scikit-learn)
│   ├── schemas.py               # Pydantic data models (20+ schemas)
│   ├── data_pipeline.py         # Feature engineering & normalization
│   ├── risk_predictor.py        # Risk prediction engine
│   ├── recommendation_engine.py # Intervention recommendations
│   ├── alert_system.py          # Alert detection & management
│   └── insights_generator.py    # Dashboard insights & reports
│
└── model/
    └── best_student_performance_model.pkl  # Trained model
```

---

## Core Modules Overview

### 1. **data_pipeline.py** - Data Preparation
Handles:
- Trend analysis (PACE completion, attendance)
- Anomaly detection (sudden score drops)
- Feature normalization (0-1 scale)
- Missing data handling

**Key Functions**:
- `calculate_pace_trend()` - PACE trend analysis
- `calculate_attendance_trend()` - Attendance pattern analysis
- `detect_score_decline()` - Identify declining subjects
- `normalize_features()` - Scale features for model
- `prepare_student_data()` - Complete data preparation

---

### 2. **risk_predictor.py** - Risk Analysis
Calculates:
- Risk probability (0-100%)
- Confidence scores (0-100%)
- Early warning indicators
- Risk factors and positive factors
- Predicted drop-off week

**Key Classes**:
- `RiskPredictor` - Main prediction engine
  - `predict_student_risk()` - Single student analysis
  - `predict_cohort_risk()` - Batch analysis
  - `_identify_early_warnings()` - Warning detection
  - `_calculate_confidence()` - Confidence scoring

**Output Example**:
```python
{
    'student_id': 'S001',
    'risk_probability': 72.5,          # 72.5% chance of falling behind
    'risk_level': 'high',              # Categorized as high-risk
    'confidence': 85.0,                # Model is 85% confident
    'early_warnings': [                # Early indicators detected
        {'type': 'pace_low', 'severity': 'high'},
        {'type': 'attendance_concerning', 'severity': 'medium'}
    ],
    'risk_factors': [                  # Contributing factors
        'Low PACE completion: 56%',
        'Below-target attendance: 82%'
    ],
    'positive_factors': [              # Strengths
        'Consistent submission: 15 on-time submissions'
    ]
}
```

---

### 3. **recommendation_engine.py** - Intervention Suggestions
Generates:
- Personalized intervention recommendations
- Priority-ordered action items
- Peer study group recommendations
- Teacher assignment suggestions

**Key Classes**:
- `RecommendationEngine` - Recommendation generation
  - `generate_recommendations()` - Top 5 recommended actions
  - `recommend_grouping()` - Peer study groups
  - `recommend_teachers()` - Best-suited teachers

**Output Example**:
```python
[
    {
        'type': 'tutoring',
        'priority': 'high',
        'action': 'Schedule 1-on-1 tutoring session for Math concepts',
        'context': 'Math score needs improvement (65%) - recommend targeted tutoring',
        'frequency': 'weekly',
        'urgency': 'immediate'
    },
    {
        'type': 'check_in',
        'priority': 'high',
        'action': 'Increase check-in frequency - identify learning blockers',
        'frequency': 'weekly',
        'urgency': 'normal'
    }
]
```

---

### 4. **alert_system.py** - Auto-Alerts
Detects:
- Risk threshold breaches (>65% risk)
- High-confidence warnings
- Status escalations (from medium to high risk)
- Cohort-level crises

**Key Classes**:
- `AlertSystem` - Alert generation and tracking
  - `check_student_alerts()` - Individual alerts
  - `check_cohort_alerts()` - Cohort-level alerts
  - `log_alert()` - Alert history tracking

**Alert Severity Levels**:
- `INFO` - Informational alerts
- `WARNING` - Moderate attention needed
- `CRITICAL` - Immediate action required

---

### 5. **insights_generator.py** - Dashboard & Reports
Generates:
- Dashboard insight cards (with icons & actions)
- Anomaly detection (sudden drops, unexpected successes)
- Outcome forecasting (graduation rates)
- Human-readable text reports

**Key Classes**:
- `InsightsGenerator` - Insights and reports
  - `generate_dashboard_insights()` - Smart cards for UI
  - `detect_anomalies()` - Unusual patterns
  - `forecast_outcomes()` - End-of-quarter predictions
  - `generate_text_report()` - Formatted reports

**Insight Card Example**:
```python
{
    'type': 'risk_status',
    'icon': '⚠️',
    'title': '2 students at risk of falling behind',
    'description': 'Immediate intervention needed for 2 student(s)',
    'action': 'Focus on 2 high-risk student(s) this week',
    'priority': 'high'
}
```

---

## Usage Examples

### Example 1: Check Single Student Risk
```python
import requests
import json

student_data = {
    "student_id": "S001",
    "pace_history": [45, 50, 55, 60, 58, 56, 54, 52],
    "attendance_history": [90, 92, 88, 85, 80, 78, 75, 72],
    "test_scores": {
        "math": [70, 72, 68, 65, 62],
        "english": [75, 76, 74, 72],
        "science": [80, 82, 81, 80]
    },
    "absences_current": 2,
    "late_arrivals_current": 1,
    "submissions": {"ontime": 15, "late": 2},
    "teacher_notes": "Struggling with math, improving in english"
}

response = requests.post(
    "http://localhost:8000/api/ai/predict-risk/",
    json=student_data
)

result = response.json()
print(f"Risk: {result['risk_probability']}%")
print(f"Level: {result['risk_level']}")
print(f"Warnings: {len(result['early_warnings'])} detected")

# Get recommendations
recommendations = requests.post(
    "http://localhost:8000/api/ai/recommend-action/",
    json=student_data
).json()

print("\nRecommended Actions:")
for rec in recommendations['recommendations']:
    print(f"- [{rec['priority'].upper()}] {rec['action']}")
```

---

### Example 2: Cohort Dashboard Insights
```python
import requests

cohort_data = {
    "cohort_id": "Section A",
    "students": [
        {
            "student_id": f"S{i:03d}",
            "pace_history": [45 + i*2, 50 + i*2, 55 + i*2],
            "attendance_history": [85 + i, 88 + i, 90 + i],
            "test_scores": {"math": [65 + i*2, 68 + i*2, 70 + i*2]},
            "absences_current": max(0, 3 - i),
            "late_arrivals_current": 0,
            "submissions": {"ontime": 15 + i, "late": max(0, 5 - i)}
        }
        for i in range(5)
    ]
}

# Get all insights at once
response = requests.post(
    "http://localhost:8000/api/ai/insights/",
    json=cohort_data
)

insights_data = response.json()

print("DASHBOARD INSIGHTS")
print("=" * 50)

for insight in insights_data['insights']:
    print(f"\n{insight['icon']} {insight['title']}")
    print(f"   {insight['description']}")
    print(f"   Action: {insight['action']}")
    print(f"   Priority: {insight['priority']}")

print("\n\nRISK SUMMARY")
print("=" * 50)
summary = insights_data['cohort_summary']
print(f"Total Students: {summary['total_students']}")
print(f"High Risk: {summary['high_risk_count']}")
print(f"Average Risk: {summary['average_risk']}%")

print("\n\nALERTS")
print("=" * 50)
alerts = insights_data['alerts']
print(f"Total Alerts: {alerts['total_alerts']}")
print(f"Critical: {alerts['critical_count']}")
```

---

### Example 3: Daily Alert Check
```python
import requests

# Load cohort
cohort_data = {...}  # Your cohort data

# Check for alerts
response = requests.post(
    "http://localhost:8000/api/ai/check-alerts/",
    json=cohort_data
)

alerts = response.json()

print("TODAY'S ALERTS")
print("=" * 50)

# Cohort-level alerts
if alerts['cohort_level']:
    print("\n⚠️  COHORT-LEVEL ALERTS:")
    for alert in alerts['cohort_level']:
        print(f"  - {alert['message']}")
        print(f"    Recommended: {alert.get('recommended_action', 'N/A')}")

# Individual alerts (critical only)
critical = [a for a in alerts['individual'] if a['severity'] == 'critical']
if critical:
    print(f"\n🚨 CRITICAL INDIVIDUAL ALERTS ({len(critical)} students):")
    for alert in critical:
        print(f"  - {alert['student_id']}: {alert['message']}")

warning = [a for a in alerts['individual'] if a['severity'] == 'warning']
if warning:
    print(f"\n⚠️  WARNING ALERTS ({len(warning)} students):")
    for alert in warning[:3]:  # Show first 3
        print(f"  - {alert['student_id']}: {alert['message']}")
```

---

### Example 4: Generate Weekly Report
```python
import requests

# Current week's data
current = {
    "cohort_id": "Section A Week 10",
    "students": [...]
}

# Previous week's data
previous = {
    "cohort_id": "Section A Week 9",
    "students": [...]
}

response = requests.post(
    "http://localhost:8000/api/ai/report/text",
    json={
        "cohort_id": "Section A",
        "students": current['students'],
        "previous_data": previous
    }
)

report = response.json()['report']

# Save to file
with open("weekly_report.txt", "w") as f:
    f.write(report)

print("Report saved to weekly_report.txt")
print("\n" + report)
```

---

### Example 5: Peer Study Group Recommendations
```python
import requests

cohort_data = {...}

response = requests.post(
    "http://localhost:8000/api/ai/grouping-recommendation/",
    json=cohort_data
)

grouping = response.json()

print("PEER STUDY GROUPS")
print("=" * 50)

for group in grouping['groupings']:
    print(f"\n{group['group_name']}")
    if group.get('mentor'):
        print(f"  Mentor: {group['mentor']}")
        print(f"  Mentees: {', '.join(group['mentees'])}")
    else:
        print(f"  Members: {', '.join(group['members'])}")
    print(f"  Focus: {group['focus']}")
    print(f"  Frequency: {group['frequency']}")

print(f"\n\nPeer Tutors Available: {', '.join(grouping['peer_tutors'])}")
```

---

## Integration with Your Dashboard

### Frontend Integration Points

#### 1. Risk Score Display
```jsx
// Show risk badge in student row
<RiskBadge
  risk={riskData.risk_level}
  probability={riskData.risk_probability}
  confidence={riskData.confidence}
/>
```

#### 2. Dashboard Insights
```jsx
// Add insight cards to dashboard
{insights.map(insight => (
  <InsightCard
    icon={insight.icon}
    title={insight.title}
    description={insight.description}
    priority={insight.priority}
    action={insight.action}
  />
))}
```

#### 3. Alert Center
```jsx
// Display alerts
<AlertCenter
  criticalAlerts={alerts.critical_count}
  alerts={alerts.individual}
  onAlertClick={handleAlertClick}
/>
```

#### 4. Recommendations Panel
```jsx
// Show actionable recommendations
<RecommendationPanel
  recommendations={recommendations}
  onActOn={handleActionTaken}
/>
```

---

## Testing the API

### 1. Using Swagger UI
Visit `http://localhost:8000/docs` and test endpoints interactively

### 2. Using cURL
```bash
# Check health
curl http://localhost:8000/api/ai/health

# Get system info
curl http://localhost:8000/api/ai/info

# Test risk prediction
curl -X POST http://localhost:8000/api/ai/predict-risk/ \
  -H "Content-Type: application/json" \
  -d @student_data.json
```

### 3. Using Python Requests
See usage examples above

---

## Performance Optimization

### 1. Batch Operations
Use batch endpoints for multiple students - 3-4x faster than individual calls

### 2. Caching
```python
from functools import lru_cache

# Cache predictions for 1 hour
@lru_cache(maxsize=1000)
def get_cached_prediction(student_id, week):
    return request_prediction(student_id, week)
```

### 3. Data Pipeline Efficiency
- Pre-compute trends in database
- Use vectorized operations for large cohorts
- Cache normalization factors

---

## Troubleshooting

### Model Not Loading
**Error**: `FileNotFoundError: best_student_performance_model.pkl`

**Solution**: Ensure model file exists in `model/` directory

### Slow Predictions
**Cause**: Processing too many students sequentially

**Solution**: Use batch endpoints or increase timeout

### Invalid Data Error
**Cause**: Missing required fields in student data

**Solution**: Ensure all fields are present, use defaults if needed:
```python
student_data = {
    "student_id": "S001",
    "pace_history": [50],  # Default values
    "attendance_history": [80],
    "test_scores": {},
    "absences_current": 0,
    "late_arrivals_current": 0,
    "submissions": {"ontime": 0, "late": 0},
    "teacher_notes": ""
}
```

---

## Next Steps

1. **Test Endpoints**: Use Swagger UI to test each endpoint
2. **Integrate with Dashboard**: Add risk badges and insight cards
3. **Set Up Alerts**: Implement alert notifications
4. **Schedule Reports**: Set up weekly automated reports
5. **Monitor Performance**: Track prediction accuracy over time

---

## Support & Documentation

- **API Docs**: See `API_DOCUMENTATION.md`
- **System Architecture**: See `ARCHITECTURE.md` (to be created)
- **Code Comments**: Detailed docstrings in each module

---

## What's Next (Phase 2+)

- [ ] Natural language chatbot for Q&A
- [ ] Model retraining pipeline
- [ ] Teacher feedback integration
- [ ] Parent communication features
- [ ] Custom alert rules
- [ ] Advanced visualization charts
