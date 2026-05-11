# LBCA AI Monitoring System - API Documentation

## Overview

The LBCA AI Monitoring System provides comprehensive student risk prediction, intervention recommendation, and cohort analysis capabilities. All endpoints accept JSON data and return structured JSON responses.

**Base URL**: `http://localhost:8000`  
**Version**: 1.0.0

---

## Quick Start

### 1. Single Student Risk Prediction

```bash
curl -X POST "http://localhost:8000/api/ai/predict-risk/" \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "S001",
    "pace_history": [45, 50, 55, 60, 58, 56],
    "attendance_history": [90, 92, 88, 85, 80, 78],
    "test_scores": {
      "math": [70, 72, 68, 65],
      "english": [75, 76, 74, 72],
      "science": [80, 82, 81, 80]
    },
    "absences_current": 2,
    "late_arrivals_current": 1,
    "submissions": {"ontime": 15, "late": 2},
    "teacher_notes": "Student showing signs of struggle with math concepts"
  }'
```

**Response**:
```json
{
  "student_id": "S001",
  "risk_probability": 72.5,
  "risk_level": "high",
  "confidence": 85.0,
  "early_warnings": [
    {
      "type": "pace_low",
      "message": "PACE completion below target: 56%",
      "severity": "high"
    },
    {
      "type": "attendance_concerning",
      "message": "Attendance concerning: 82%",
      "severity": "medium"
    }
  ],
  "predicted_drop_week": 8,
  "risk_factors": [
    "Low PACE completion: 56%",
    "Below-target attendance: 82%",
    "Math proficiency concerns: 65%"
  ],
  "positive_factors": [
    "Consistent submission: 15 on-time submissions"
  ],
  "trends": {
    "pace_trend": -3.5,
    "pace_direction": "declining",
    "attendance_info": {
      "trend": "concerning",
      "risk_level": "medium",
      "avg": 82.0
    },
    "declining_subjects": ["math"]
  }
}
```

### 2. Batch Cohort Analysis

```bash
curl -X POST "http://localhost:8000/api/ai/predict-risk/batch/" \
  -H "Content-Type: application/json" \
  -d '{
    "cohort_id": "Section A",
    "students": [
      {
        "student_id": "S001",
        "pace_history": [45, 50, 55],
        "attendance_history": [90, 92, 88],
        "test_scores": {"math": [70, 72, 68]},
        "absences_current": 2,
        "late_arrivals_current": 1,
        "submissions": {"ontime": 15, "late": 2}
      },
      {
        "student_id": "S002",
        "pace_history": [80, 82, 85],
        "attendance_history": [95, 96, 95],
        "test_scores": {"math": [85, 88, 90]},
        "absences_current": 0,
        "late_arrivals_current": 0,
        "submissions": {"ontime": 20, "late": 0}
      }
    ]
  }'
```

---

## Endpoint Categories

### A. Risk Prediction Endpoints

#### 1. `POST /api/ai/predict-risk/`
**Predict risk for a single student**

**Request Body**:
```json
{
  "student_id": "string (required)",
  "pace_history": [float] (optional, default: [50]),
  "attendance_history": [float] (optional, default: [80]),
  "test_scores": {
    "math": [float],
    "english": [float],
    "science": [float]
  } (optional),
  "absences_current": int (optional, default: 0),
  "late_arrivals_current": int (optional, default: 0),
  "submissions": {
    "ontime": int,
    "late": int
  } (optional),
  "teacher_notes": "string" (optional)
}
```

**Response**: `RiskAnalysis` object with:
- `risk_probability`: 0-100 scale
- `risk_level`: "low" | "medium" | "high"
- `confidence`: 0-100 scale
- `early_warnings`: List of warning indicators
- `risk_factors`: Contributing factors to risk
- `positive_factors`: Strengths supporting success
- `trends`: Trend analysis

**Use Case**: Get risk score for individual student profile

---

#### 2. `POST /api/ai/predict-risk/batch/`
**Predict risk for multiple students**

**Request Body**: Same as above but wrapped in:
```json
{
  "cohort_id": "string (optional)",
  "students": [StudentDataInput]
}
```

**Response**: `CohortRiskSummary` with:
- `total_students`: int
- `risk_distribution`: {"low": N, "medium": N, "high": N}
- `high_risk_count`: int
- `average_risk`: float
- `average_confidence`: float
- `predictions`: [RiskAnalysis]
- `critical_students`: [RiskAnalysis]

**Use Case**: Cohort-level risk overview for dashboard/reporting

---

### B. Recommendation Endpoints

#### 3. `POST /api/ai/recommend-action/`
**Get intervention recommendations for a student**

**Request Body**: `StudentDataInput`

**Response**: `RecommendationSet` with:
```json
{
  "student_id": "S001",
  "recommendations": [
    {
      "type": "tutoring|peer_study|check_in|parent_contact|content_review|grouping|teacher_support|pace_extension",
      "priority": "critical|high|medium|low",
      "action": "Schedule 1-on-1 tutoring session for Math concepts",
      "context": "Math score needs improvement - recommend targeted math tutoring",
      "frequency": "weekly|bi-weekly|as-needed|immediate",
      "confidence_score": 85.0,
      "urgency": "immediate|normal"
    }
  ]
}
```

**Use Case**: Get specific action items for student intervention

---

#### 4. `POST /api/ai/grouping-recommendation/`
**Recommend peer study groups and mentoring**

**Request Body**: `CohortDataInput`

**Response**: `GroupingRecommendation` with:
```json
{
  "total_groups": 5,
  "groupings": [
    {
      "group_name": "Study Group 1",
      "mentor": "S002",
      "mentees": ["S001"],
      "focus": "Low PACE completion: 56%",
      "frequency": "twice weekly"
    }
  ],
  "mentorship_opportunities": 3,
  "peer_tutors": ["S002", "S010", "S015"]
}
```

**Use Case**: Form peer study groups for collaborative learning

---

### C. Alert & Monitoring Endpoints

#### 5. `POST /api/ai/check-alerts/`
**Check for alert conditions in cohort**

**Request Body**: `CohortDataInput`

**Response**: `AlertSummary` with:
```json
{
  "total_alerts": 8,
  "critical_count": 2,
  "cohort_level": [
    {
      "severity": "critical",
      "type": "cohort_crisis",
      "message": "High-risk percentage (35%) exceeds threshold - intervention needed",
      "timestamp": "2026-05-11T10:30:00",
      "actionable": true
    }
  ],
  "individual": [
    {
      "student_id": "S001",
      "severity": "critical",
      "type": "high_risk_detected",
      "message": "Student at 72.5% risk of falling behind",
      "recommended_action": "Schedule intervention meeting with student and parents",
      "actionable": true
    }
  ]
}
```

**Use Case**: Daily alert check for urgent interventions needed

---

#### 6. `GET /api/ai/alerts/student/{student_id}`
**Get alert history for a student**

**Query Parameters**:
- `limit`: int (default: 10) - Number of alerts to return

**Response**:
```json
{
  "student_id": "S001",
  "alert_count": 5,
  "alerts": [...]
}
```

**Use Case**: Track historical alerts for a student

---

#### 7. `GET /api/ai/alerts/active`
**Get all currently active alerts**

**Query Parameters**:
- `severity`: "critical" | "warning" | "info" (optional)

**Response**:
```json
{
  "total": 3,
  "severity_filter": "critical",
  "alerts": [...]
}
```

**Use Case**: Dashboard alert center showing all urgent items

---

### D. Insights & Analysis Endpoints

#### 8. `POST /api/ai/insights/`
**Get comprehensive dashboard insights**

**Request Body**: `CohortDataInput`

**Response**: `CohortAnalysisResponse` with:
```json
{
  "cohort_summary": {...},
  "insights": [
    {
      "type": "section_comparison",
      "icon": "📊",
      "title": "Section A outperforming by 15%",
      "description": "4 students performing well - consider best practices study",
      "action": "Review successful strategies with 4 high-performing students",
      "priority": "medium"
    },
    {
      "type": "risk_status",
      "icon": "⚠️",
      "title": "2 students at risk of falling behind",
      "description": "Immediate intervention needed for 2 student(s)",
      "action": "Focus on 2 high-risk student(s) this week",
      "priority": "high"
    },
    {
      "type": "trend",
      "icon": "📈",
      "title": "PACE completion trending up — momentum continuing",
      "description": "5 students showing improvement trends",
      "action": "Maintain current pace and support level",
      "priority": "low"
    },
    {
      "type": "actions",
      "icon": "🔔",
      "title": "5 critical alerts need attention today",
      "description": "2 high-risk + 3 medium-risk students",
      "action": "Review priority interventions in Alert Center",
      "priority": "critical"
    }
  ],
  "alerts": {...},
  "anomalies": [...],
  "forecast": {...}
}
```

**Use Case**: All-in-one dashboard insights call

---

#### 9. `POST /api/ai/anomalies/`
**Detect unusual performance patterns**

**Request Body**: `CohortDataInput`

**Response**: List of `Anomaly` objects
```json
{
  "type": "sudden_drop|unexpected_success",
  "student_id": "S001",
  "description": "PACE dropping rapidly (-15.0% per week)",
  "severity": "high|low",
  "recommendation": "Investigate reason for sudden drop immediately"
}
```

**Use Case**: Surface unusual behaviors for investigation

---

#### 10. `POST /api/ai/forecast/`
**Forecast end-of-quarter outcomes**

**Request Body**: `CohortDataInput`

**Response**: `OutcomeForecast`
```json
{
  "total_students": 30,
  "predicted_pass": 27,
  "predicted_at_risk": 3,
  "predicted_pass_rate": 90.0,
  "confidence": 0.75
}
```

**Use Case**: Long-term planning and outcome prediction

---

#### 11. `POST /api/ai/analyze-pattern/`
**Analyze patterns in cohort performance**

**Request Body**: `CohortDataInput`

**Response**:
```json
{
  "cohort_id": "Section A",
  "total_students": 30,
  "patterns": {
    "pace_declining_count": 5,
    "pace_improving_count": 12,
    "attendance_issues": 3,
    "subject_struggles": {
      "math": 4,
      "english": 2
    }
  },
  "recommendations": "Focus on students with declining PACE and attendance patterns"
}
```

**Use Case**: Identify systemic issues and strengths in cohort

---

### E. Reporting Endpoints

#### 12. `POST /api/ai/report/text`
**Generate human-readable text report**

**Request Body**:
```json
{
  "cohort_id": "Section A",
  "students": [...],
  "previous_data": {
    "cohort_id": "Section A Previous Week",
    "students": [...]
  } (optional)
}
```

**Response**:
```json
{
  "report": "============================================================\nLBCA MONITORING SYSTEM - WEEKLY PERFORMANCE REPORT\n...[formatted text report]...",
  "generated_at": "2026-05-11T10:30:00"
}
```

**Use Case**: Email reports, PDF generation, administrative summaries

---

### F. System Health Endpoints

#### 13. `GET /api/ai/health`
**Check AI system health**

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2026-05-11T10:30:00",
  "modules": {
    "data_pipeline": "active",
    "risk_predictor": "active",
    "recommendation_engine": "active",
    "alert_system": "active",
    "insights_generator": "active"
  }
}
```

---

#### 14. `GET /api/ai/info`
**Get system information**

**Response**:
```json
{
  "system": "LBCA AI Monitoring System",
  "version": "1.0.0",
  "features": [
    "Student risk prediction with confidence scores",
    "Early warning indicators",
    "Intervention recommendations",
    "Cohort-level analysis and anomaly detection",
    "Automatic alert generation",
    "Dashboard insights and trend forecasting",
    "Text report generation"
  ],
  "models": {
    "risk_prediction": "Random Forest (scikit-learn)",
    "feature_engineering": "7-day trend analysis"
  }
}
```

---

## Legacy Endpoints

### `POST /predict`
**Legacy simple prediction endpoint**

**Request**:
```json
{
  "features": [float, float, ..., float]  // 10 features
}
```

**Response**:
```json
{
  "prediction": [float]
}
```

---

## Data Input Format Reference

### Student Weekly Data Template

```json
{
  "student_id": "S001",
  "current_week": 10,
  
  "pace_history": [45, 50, 55, 60, 58, 56, 54, 52, 50, 48],
  // Weekly PACE completion percentage (0-100)
  
  "attendance_history": [90, 92, 88, 85, 80, 82, 78, 75, 72, 70],
  // Weekly attendance percentage (0-100)
  
  "test_scores": {
    "math": [70, 72, 68, 65, 62, 60],
    "english": [75, 76, 74, 72, 70],
    "science": [80, 82, 81, 80, 79]
  },
  // Subject scores (0-100) - can include multiple assessments
  
  "absences_current": 2,
  // Number of absences in current period
  
  "late_arrivals_current": 1,
  // Number of late arrivals in current period
  
  "submissions": {
    "ontime": 15,
    "late": 2
  },
  // Assignment submission tracking
  
  "teacher_notes": "Student struggling with math concepts, shows promise in other areas"
  // Qualitative feedback - keywords: struggle, concern, behind, issue, problem
}
```

---

## Error Handling

All endpoints return HTTP status codes:
- **200**: Success
- **400**: Bad request (invalid data format)
- **404**: Not found
- **500**: Server error

Error response format:
```json
{
  "detail": "Error message describing what went wrong"
}
```

---

## Integration Examples

### Example 1: Daily Risk Check
```python
import requests

# Get cohort data (from your database)
cohort_data = {
    "cohort_id": "Section A",
    "students": [...]  # Student data
}

# Check alerts
response = requests.post(
    "http://localhost:8000/api/ai/check-alerts/",
    json=cohort_data
)

alerts = response.json()

# Process critical alerts
for alert in alerts['individual']:
    if alert['severity'] == 'critical':
        # Send notification, log event, etc.
        print(f"CRITICAL: {alert['student_id']} - {alert['message']}")
```

### Example 2: Dashboard Insights
```python
# Get comprehensive insights
response = requests.post(
    "http://localhost:8000/api/ai/insights/",
    json=cohort_data
)

insights_response = response.json()

# Display insight cards
for insight in insights_response['insights']:
    print(f"{insight['icon']} {insight['title']}")
    print(f"   {insight['description']}")
```

### Example 3: Generate Weekly Report
```python
# Get this week's data
this_week_data = {...}

# Get last week's data
last_week_data = {...}

# Generate comparative report
response = requests.post(
    "http://localhost:8000/api/ai/report/text",
    json={
        "students": this_week_data['students'],
        "previous_data": last_week_data
    }
)

report = response.json()['report']

# Save or email report
with open("weekly_report.txt", "w") as f:
    f.write(report)
```

---

## Performance Metrics

- **Single student prediction**: ~50ms
- **Batch cohort analysis (30 students)**: ~200ms
- **Dashboard insights generation**: ~300ms
- **Alert check**: ~100ms

---

## Best Practices

1. **Batch Operations**: Use batch endpoints for cohort analysis - more efficient than individual calls
2. **Caching**: Cache risk predictions for 1-2 hours to reduce computation
3. **Alert Handling**: Log all alerts and track resolution for analysis
4. **Data Quality**: Ensure historical data is current and accurate
5. **Regular Reports**: Generate weekly reports for trend tracking

---

## Future Endpoints (Phase 2+)

- `POST /api/ai/retrain-model/` - Trigger model retraining
- `POST /api/ai/chat/` - AI chatbot for questions about students
- `POST /api/ai/similar-students/` - Find similar student cohorts
- `GET /api/ai/teacher/{teacher_id}/students` - Get students assigned to teacher
- `POST /api/ai/intervention-outcome/` - Log intervention results for feedback

---

## Support

For issues or questions:
1. Check system health: `GET /api/ai/health`
2. Review request format against schema
3. Check error message for specific issue
4. Verify data completeness and accuracy
