from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime

# ==================== Input Schemas ====================

class StudentInput(BaseModel):
    """Legacy input for simple predictions"""
    features: List[float]

class StudentDataInput(BaseModel):
    """Comprehensive student data for risk analysis"""
    student_id: str
    current_week: Optional[int] = None
    pace_history: Optional[List[float]] = []
    attendance_history: Optional[List[float]] = []
    test_scores: Optional[Dict[str, List[float]]] = {}
    absences_current: Optional[int] = 0
    late_arrivals_current: Optional[int] = 0
    submissions: Optional[Dict[str, int]] = {"ontime": 0, "late": 0}
    teacher_notes: Optional[str] = ""

class CohortDataInput(BaseModel):
    """Multiple students for cohort analysis"""
    students: List[StudentDataInput]
    cohort_id: Optional[str] = None

# ==================== Risk Analysis Output Schemas ====================

class RiskTrendInfo(BaseModel):
    """Trend information for a student"""
    pace_trend: float
    pace_direction: str  # 'improving', 'stable', 'declining'
    attendance_info: Dict
    declining_subjects: List[str]

class EarlyWarning(BaseModel):
    """Early warning indicator"""
    type: str
    message: str
    severity: str  # 'critical', 'high', 'medium', 'low'

class RiskAnalysis(BaseModel):
    """Complete risk analysis for a student"""
    student_id: str
    risk_probability: float  # 0-100
    risk_level: str  # 'low', 'medium', 'high'
    confidence: float  # 0-100
    early_warnings: List[EarlyWarning] = []
    predicted_drop_week: Optional[int] = None
    risk_factors: List[str] = []
    positive_factors: List[str] = []
    trends: RiskTrendInfo

class CohortRiskSummary(BaseModel):
    """Summary of risk analysis for a cohort"""
    total_students: int
    risk_distribution: Dict[str, int]  # {'low': X, 'medium': Y, 'high': Z}
    high_risk_count: int
    average_risk: float
    average_confidence: float
    predictions: List[RiskAnalysis]
    critical_students: List[RiskAnalysis]

# ==================== Recommendation Schemas ====================

class Recommendation(BaseModel):
    """Single intervention recommendation"""
    type: str  # InterventionType enum value
    priority: str  # 'critical', 'high', 'medium', 'low'
    action: str
    context: str
    frequency: str  # 'immediate', 'weekly', 'bi-weekly', etc.
    confidence_score: float
    urgency: str

class RecommendationSet(BaseModel):
    """Set of recommendations for a student"""
    student_id: str
    recommendations: List[Recommendation]
    next_review: Optional[datetime] = None

class StudentGrouping(BaseModel):
    """Peer study or mentoring group"""
    group_name: str
    mentor: Optional[str] = None
    mentees: Optional[List[str]] = None
    members: Optional[List[str]] = None
    focus: str
    frequency: str

class GroupingRecommendation(BaseModel):
    """Grouping recommendations for cohort"""
    total_groups: int
    groupings: List[StudentGrouping]
    mentorship_opportunities: int
    peer_tutors: List[str]

# ==================== Alert Schemas ====================

class Alert(BaseModel):
    """Single alert"""
    student_id: str
    severity: str  # 'info', 'warning', 'critical'
    type: str
    message: str
    timestamp: str
    risk_level: Optional[str] = None
    confidence: Optional[float] = None
    actionable: bool
    recommended_action: str

class AlertSummary(BaseModel):
    """Summary of alerts"""
    total_alerts: int
    critical_count: int
    cohort_level: List[Alert] = []
    individual: List[Alert] = []

# ==================== Insights Schemas ====================

class InsightCard(BaseModel):
    """Dashboard insight card"""
    type: str
    icon: str
    title: str
    description: str
    action: str
    priority: str  # 'low', 'medium', 'high', 'critical'

class Anomaly(BaseModel):
    """Detected anomaly in student performance"""
    type: str  # 'sudden_drop', 'unexpected_success'
    student_id: str
    description: str
    severity: str
    recommendation: str

class OutcomeForecast(BaseModel):
    """Forecasted outcomes for cohort"""
    total_students: int
    predicted_pass: int
    predicted_at_risk: int
    predicted_pass_rate: float
    confidence: float

# ==================== API Response Schemas ====================

class PredictionOutput(BaseModel):
    """Legacy output"""
    prediction: List[float]

class RiskPredictionResponse(BaseModel):
    """Response from risk prediction endpoint"""
    risk_analysis: RiskAnalysis
    recommendations: List[Recommendation]
    alerts: List[Alert]

class CohortAnalysisResponse(BaseModel):
    """Response from cohort analysis endpoint"""
    cohort_summary: CohortRiskSummary
    insights: List[InsightCard]
    alerts: AlertSummary
    anomalies: List[Anomaly]
    forecast: OutcomeForecast

class TextReportResponse(BaseModel):
    """Text report response"""
    report: str
    generated_at: str

# ==================== Batch Operation Schemas ====================

class BatchPredictionRequest(BaseModel):
    """Request for batch predictions"""
    students: List[StudentDataInput]
    return_recommendations: bool = True
    return_insights: bool = False

class BatchPredictionResponse(BaseModel):
    """Response from batch predictions"""
    processed: int
    predictions: List[RiskAnalysis]
    summary: CohortRiskSummary