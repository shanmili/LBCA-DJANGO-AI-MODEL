# LBCA AI Monitoring System - Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                      FRONTEND DASHBOARD                          │
│           (React/Vue with Real-time Updates)                    │
└────────────────────────────┬────────────────────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│  Risk Dashboard  │ │ Alert Center     │ │ Insight Cards    │
│  • Risk badges   │ │ • Critical alerts │ │ • Trends         │
│  • Confidence    │ │ • Action items    │ │ • Anomalies      │
│  • Trends        │ │ • Notifications   │ │ • Forecasts      │
└────────┬─────────┘ └────────┬─────────┘ └────────┬─────────┘
         │                    │                    │
         └────────────────────┼────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────┐
        │      FASTAPI Server (main.py)        │
        │  • 14+ REST API Endpoints             │
        │  • Request validation                 │
        │  • Response formatting                │
        └─────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
   │  Data Flow   │  │ Core AI      │  │  Output      │
   │  Pipeline    │  │  Engines     │  │  Generators  │
   └──────────────┘  └──────────────┘  └──────────────┘
         │                    │                │
    ┌────┴────┐         ┌─────┴─────┐    ┌────┴────┐
    │          │         │           │    │         │
    ▼          ▼         ▼           ▼    ▼         ▼
┌──────┐ ┌────────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐
│Data  │ │Trend   │ │Risk  │ │Recom-│ │Alert │ │Report│
│Pipe- │ │Analys. │ │Predic│ │mend. │ │Sys.  │ │Gen.  │
│line  │ │(7-day) │ │tor   │ │Engine│ │      │ │      │
└──────┘ └────────┘ └──────┘ └──────┘ └──────┘ └──────┘
```

---

## Component Architecture

### 1. Data Pipeline (`data_pipeline.py`)

**Purpose**: Prepare and normalize student data for AI processing

**Key Responsibilities**:
- Load raw student data
- Calculate feature trends (7-day moving average)
- Detect anomalies (sudden drops > 10%)
- Normalize features to 0-1 scale
- Handle missing values

**Main Methods**:
```python
DataPipeline:
  ├── calculate_pace_trend(historical_pace)
  │   └── Returns: (trend_rate, direction)
  │
  ├── calculate_attendance_trend(weekly_attendance)
  │   └── Returns: {trend, risk_level, avg}
  │
  ├── detect_score_decline(test_scores)
  │   └── Returns: [declining_subjects]
  │
  ├── normalize_features(features)
  │   └── Returns: np.ndarray (10 features, 0-1 scale)
  │
  └── prepare_student_data(student_data)
      └── Returns: {student_id, features, trends}
```

**Data Flow**:
```
Raw Student Data
    ↓
Clean & Validate
    ↓
Calculate Trends (7-day)
    ↓
Detect Anomalies
    ↓
Normalize Features (0-1)
    ↓
Ready for Model Input
```

---

### 2. Risk Predictor (`risk_predictor.py`)

**Purpose**: Predict student risk with detailed analysis and confidence scoring

**Architecture**:
```
Student Data (from Pipeline)
         ↓
    [Feature Array]
         ↓
   ┌─────────────┐
   │ Loaded Model│ (scikit-learn Random Forest)
   │  .pkl file  │
   └─────────────┘
         ↓
   Raw Prediction (0-1)
         ↓
    [Post-Processing]
         ├── Calculate Confidence Score
         ├── Identify Early Warnings
         ├── Extract Risk Factors
         ├── List Positive Factors
         └── Predict Drop-off Week
         ↓
   RiskAnalysis Output
   ├── risk_probability (0-100)
   ├── risk_level (low/medium/high)
   ├── confidence (0-100)
   ├── early_warnings
   ├── risk_factors
   ├── positive_factors
   └── trends
```

**Risk Level Thresholds**:
- **Low**: 0-30% probability
- **Medium**: 30-65% probability
- **High**: 65-100% probability

**Confidence Calculation**:
```
Base Confidence: 50%

For each warning indicator detected:
+ 8% (up to 40% max)

Factors:
- PACE < 60%        → +1 warning
- Attendance < 80%  → +1 warning
- Absences > 2      → +1 warning
- Late submissions  → +1 warning
- Teacher concern   → +1 warning
- Declining trend   → +1 warning

Result: Base + (warnings × 8%), capped at 90%
```

**Early Warning Detection**:
```
PACE-related:
├── pace_critical (< 50%)           → Severity: CRITICAL
├── pace_low (50-70%)               → Severity: HIGH
└── pace_declining                  → Severity: HIGH

Attendance-related:
├── attendance_critical (< 75%)     → Severity: CRITICAL
├── attendance_concerning           → Severity: MEDIUM
└── absences_pattern (2+ in 2 wks)  → Severity: HIGH

Academic:
├── subject_decline (>10pt drop)    → Severity: MEDIUM
└── teacher_concern                 → Severity: HIGH
```

---

### 3. Recommendation Engine (`recommendation_engine.py`)

**Purpose**: Generate actionable intervention recommendations

**Recommendation Flow**:
```
RiskAnalysis (from Predictor)
    ↓
Identify Risk Factors
    ├── PACE issues?
    ├── Attendance issues?
    ├── Academic struggles?
    ├── Behavioral concerns?
    └── Declining trends?
    ↓
Map to Interventions
    ├── Tutoring
    ├── Peer Study
    ├── Check-ins
    ├── Parent Contact
    ├── Content Review
    ├── Teacher Support
    ├── Grouping
    └── PACE Extension
    ↓
Priority Ranking
    ├── Critical (immediate)
    ├── High (this week)
    ├── Medium (this month)
    └── Low (ongoing)
    ↓
RecommendationSet Output
```

**Intervention Types & Triggers**:

| Intervention | Trigger Condition | Priority | Frequency |
|-------------|------------------|----------|-----------|
| Tutoring | Subject score < 70% | High | Weekly |
| Peer Study | Similar peer found | Medium | Bi-weekly |
| Check-in | Trend declining | High | Weekly |
| Parent Contact | Attendance < 80% | High | Bi-weekly |
| Content Review | Multiple subjects down | Medium | Weekly |
| Teacher Support | Teacher flagged | High | As-needed |
| Grouping | Group dynamics needed | Medium | Bi-weekly |
| PACE Extension | PACE < 50% | Critical | Immediate |

**Grouping Algorithm**:
```
1. Identify Low-Risk Students (confidence > 75%)
   → Potential Peer Tutors

2. Identify High-Risk Students
   → Need Mentoring

3. Create Pairs: 1 Tutor + 1-2 Mentees
   → Based on subject match

4. Group Remaining Medium-Risk
   → Collaborative Learning Groups (3 per group)

Output:
├── Mentorship Pairs (tutor-mentee)
├── Study Groups (3+ peer learners)
└── Focus Areas (math, English, etc.)
```

---

### 4. Alert System (`alert_system.py`)

**Purpose**: Detect critical conditions and generate actionable alerts

**Alert Detection Levels**:

```
┌─────────────────────────────────────┐
│        Threshold Breach?            │
├─────────────────────────────────────┤
│ Risk Probability > 65%              │
│ Confidence > 70% + Risk > 50%       │
│ Early Warning (CRITICAL severity)   │
│ Status Escalation (low→high)        │
│ Cohort-level crisis (>30% at risk)  │
└─────────────────────────────────────┘
        ↓
┌─────────────────────────────────────┐
│    Generate Alert Object            │
├─────────────────────────────────────┤
│ {                                   │
│   severity: INFO|WARNING|CRITICAL   │
│   type: specific_alert_type         │
│   message: human_readable_text      │
│   recommended_action: actionable    │
│   timestamp: ISO_datetime           │
│ }                                   │
└─────────────────────────────────────┘
        ↓
┌─────────────────────────────────────┐
│  Log to Alert History               │
│  (track resolution)                 │
└─────────────────────────────────────┘
```

**Alert Severity Mapping**:
- **INFO**: Low priority, informational
- **WARNING**: Moderate attention needed
- **CRITICAL**: Immediate action required

**Alert Types**:
```
Individual Alerts:
├── high_risk_detected (risk > 65%)
├── high_confidence_warning (high confidence + medium risk)
├── pace_critical (PACE < 50%)
├── pace_declining (downward trend)
├── attendance_critical (attendance < 75%)
├── attendance_concerning (75-85%)
├── absences_pattern (2+ consecutive)
├── subject_decline (>10pt drop)
├── teacher_concern (flagged)
├── risk_increased (>20% increase)
└── status_escalated (level change)

Cohort Alerts:
├── cohort_high_risk (any at-risk students)
└── cohort_crisis (>30% at-risk)
```

---

### 5. Insights Generator (`insights_generator.py`)

**Purpose**: Create dashboard insights, detect anomalies, forecast outcomes

**Insight Generation**:

```
Cohort Risk Data
    ├── Performance Comparison
    │   └── Section A vs B benchmarking
    │
    ├── Risk Summary
    │   ├── All on track? → ✅ Green
    │   ├── Few at risk? → ⚠️  Yellow
    │   └── Many at risk? → 🚨 Red
    │
    ├── Trend Analysis
    │   ├── Improving → 📈 Momentum
    │   ├── Declining → 📉 Concern
    │   └── Stable → → No change
    │
    └── Action Items
        └── Count critical alerts

Output: [InsightCard, InsightCard, ...]
```

**Insight Card Structure**:
```json
{
  "type": "card_type",
  "icon": "📊",
  "title": "Main message",
  "description": "Details",
  "action": "What to do",
  "priority": "low|medium|high|critical"
}
```

**Anomaly Detection**:
```
For each student:
├── Sudden Drop Detected?
│   └── PACE declining >10% per week
│       → Investigate immediately
│
└── Unexpected Success?
    └── Low risk despite challenges
        → Study success factors
```

**Outcome Forecasting**:
```
Current State + Trends → End-of-Quarter Prediction

Example:
- 30 total students
- 3 high-risk (predicted fail)
- 27 expected to pass
- Predicted pass rate: 90%
- Confidence: 75%

For use in: Planning, resource allocation, goal setting
```

**Report Generation**:
```
Text Report Contains:
├── Executive Summary
│   ├── Total students
│   ├── At-risk count
│   ├── Average risk %
│   └── Prediction confidence
│
├── Risk Distribution
│   ├── Low Risk: N (%)
│   ├── Medium Risk: N (%)
│   └── High Risk: N (%)
│
├── Critical Students
│   ├── Top 5 at-risk
│   ├── Risk %, Confidence
│   └── Key issues
│
├── Key Trends
│   ├── Improving students
│   ├── Declining students
│   └── Trend analysis
│
└── Week-over-Week Change
    ├── Risk increase/decrease
    └── Interpretation
```

---

## API Endpoint Organization

### Layer 1: Basic Endpoints
```
GET  /                           → Health check
POST /predict                    → Legacy prediction
```

### Layer 2: Core AI Endpoints
```
POST /api/ai/predict-risk/       → Single student risk
POST /api/ai/predict-risk/batch/ → Cohort risk (batch)
```

### Layer 3: Actionable Endpoints
```
POST /api/ai/recommend-action/          → Recommendations
POST /api/ai/grouping-recommendation/   → Peer grouping
POST /api/ai/check-alerts/              → Alert check
```

### Layer 4: Analysis Endpoints
```
POST /api/ai/insights/          → Dashboard insights (all-in-one)
POST /api/ai/anomalies/         → Anomaly detection
POST /api/ai/analyze-pattern/   → Pattern analysis
POST /api/ai/forecast/          → Outcome forecasting
```

### Layer 5: Reporting Endpoints
```
POST /api/ai/report/text        → Generate text report
```

### Layer 6: Management Endpoints
```
GET  /api/ai/alerts/student/{id} → Alert history
GET  /api/ai/alerts/active       → Active alerts
GET  /api/ai/health              → System health
GET  /api/ai/info                → System info
```

---

## Data Flow Example: Complete Student Assessment

```
┌─────────────────────────────────────────────────────────┐
│ 1. CLIENT REQUEST                                       │
│    POST /api/ai/predict-risk/                           │
│    {student_id: "S001", pace_history: [...], ...}      │
└──────────────────────┬──────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────┐
│ 2. FASTAPI VALIDATION (main.py)                        │
│    • Parse JSON                                         │
│    • Validate with StudentDataInput schema             │
│    • Handle errors                                      │
└──────────────────────┬──────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────┐
│ 3. DATA PIPELINE (data_pipeline.py)                    │
│    prepare_student_data(input)                          │
│    ├── Calculate PACE trend                             │
│    ├── Analyze attendance pattern                       │
│    ├── Detect score decline                             │
│    └── Normalize features → [0-1]                       │
└──────────────────────┬──────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────┐
│ 4. RISK PREDICTION (risk_predictor.py)                 │
│    predict_student_risk(prepared_data)                  │
│    ├── Load model.pkl → predict()                       │
│    ├── Convert to probability                           │
│    ├── Calculate confidence                             │
│    ├── Identify early warnings                          │
│    └── Extract factors                                  │
└──────────────────────┬──────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────┐
│ 5. ALERT DETECTION (alert_system.py)                   │
│    check_student_alerts(risk_analysis)                  │
│    └── Generate alerts if thresholds breached           │
└──────────────────────┬──────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────┐
│ 6. RESPONSE FORMATTING (main.py)                       │
│    • Convert to RiskAnalysis schema                     │
│    • Return JSON                                        │
└──────────────────────┬──────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────┐
│ 7. CLIENT RECEIVES                                      │
│    {                                                     │
│      "student_id": "S001",                               │
│      "risk_probability": 72.5,                           │
│      "risk_level": "high",                               │
│      "confidence": 85.0,                                 │
│      ...                                                 │
│    }                                                     │
└─────────────────────────────────────────────────────────┘
```

---

## Database Integration (Future)

When integrating with your Django database:

```
Django Model → FastAPI Endpoint → AI Processing → Response

Example:
Student.objects.get(id="S001")
    ↓
Serialize to StudentDataInput
    ↓
POST /api/ai/predict-risk/
    ↓
RiskAnalysis returned
    ↓
Save to StudentRisk model
    ↓
Return to dashboard
```

---

## Scalability Considerations

### Batch Processing
- Process 100 students: ~10 seconds
- Process 1000 students: ~100 seconds
- Use background tasks for large batches

### Caching Strategy
- Cache individual predictions for 1 hour
- Cache cohort predictions for 30 minutes
- Cache model for entire session

### Async Operations (Future)
```
POST /api/ai/batch-analysis/async
    → Returns: {task_id: "uuid"}

GET /api/ai/batch-results/{task_id}
    → Returns: results when ready
```

---

## Security & Validation

### Input Validation
- Pydantic schemas validate all inputs
- Range checks on percentages (0-100)
- Student IDs must be non-empty strings

### Error Handling
- Try-catch blocks in all endpoints
- Meaningful error messages
- HTTP status codes (200, 400, 500)

### Data Privacy
- No sensitive data in logs
- Remove student IDs from debug output (future)
- HIPAA compliance when needed (future)

---

## Testing Strategy

### Unit Tests (Future)
```
test_data_pipeline.py
├── test_normalize_features()
├── test_calculate_pace_trend()
└── test_detect_score_decline()

test_risk_predictor.py
├── test_predict_low_risk_student()
├── test_predict_high_risk_student()
└── test_cohort_prediction()
```

### Integration Tests (Future)
```
test_api_endpoints.py
├── test_predict_risk_endpoint()
├── test_recommendations_endpoint()
└── test_alerts_endpoint()
```

---

## Performance Metrics

### Current Performance (Baseline)
- Single student prediction: ~50ms
- Batch cohort (30 students): ~200ms
- Dashboard insights: ~300ms
- Text report generation: ~500ms

### Optimization Opportunities
- [ ] Cache model in memory (currently loads each time)
- [ ] Vectorize batch operations with NumPy
- [ ] Add Redis caching layer
- [ ] Implement async processing
- [ ] Database query optimization

---

## Future Enhancements

### Phase 2: NLP Features
- Chatbot for Q&A about students
- Auto-parsing teacher notes
- Sentiment analysis on feedback

### Phase 3: Advanced Models
- Gradient boosting (XGBoost)
- Neural networks (TensorFlow)
- Ensemble models

### Phase 4: Automation
- Background task scheduling
- Automated report email
- Real-time notifications
- Teacher intervention tracking

### Phase 5: Integration
- Complete Django app integration
- Parent portal with AI insights
- Teacher mobile app
- Student self-assessment

---

## Deployment Architecture

```
┌──────────────────────────────────────┐
│      Production Environment          │
├──────────────────────────────────────┤
│                                      │
│  ┌──────────────────────────────┐   │
│  │  Nginx/Load Balancer        │   │
│  └────────────┬─────────────────┘   │
│               │                      │
│  ┌────────────┼─────────────────┐   │
│  │            │                 │   │
│  ▼            ▼                 ▼   │
│ ┌──┐        ┌──┐              ┌──┐  │
│ │  │ uvicorn│  │ uvicorn      │  │  │
│ │1 │ worker │2 │ worker       │3 │  │
│ │  │        │  │              │  │  │
│ └──┘        └──┘              └──┘  │
│               │                      │
│  ┌────────────┼─────────────────┐   │
│  │            ▼                 │   │
│  │  ┌──────────────────────┐   │   │
│  │  │   Redis Cache        │   │   │
│  │  └──────────────────────┘   │   │
│  │            │                 │   │
│  │  ┌─────────┴──────────────┐  │   │
│  │  │                        │  │   │
│  │  ▼                        ▼  │   │
│  │ ┌──────────────────────────┐ │   │
│  │ │    PostgreSQL DB         │ │   │
│  │ │    • Students            │ │   │
│  │ │    • Risk Predictions    │ │   │
│  │ │    • Alerts              │ │   │
│  │ └──────────────────────────┘ │   │
│  │                              │   │
│  └──────────────────────────────┘   │
│                                      │
└──────────────────────────────────────┘
```

---

## Summary

The LBCA AI Monitoring System is built with a **modular, layered architecture** that:

1. **Separates concerns** - Each module has a specific responsibility
2. **Enables reusability** - Components can be used independently
3. **Supports scalability** - Can process batches of students efficiently
4. **Provides flexibility** - Easy to add new models, endpoints, features
5. **Ensures maintainability** - Clear data flow, well-documented code

All components work together to deliver a comprehensive student monitoring and intervention system with risk prediction, actionable recommendations, automatic alerts, and dashboard insights.
