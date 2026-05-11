from fastapi import FastAPI, HTTPException
from typing import List, Optional
from datetime import datetime

# Import AI modules
from app.schemas import (
    StudentInput, PredictionOutput, StudentDataInput, CohortDataInput,
    RiskAnalysis, CohortRiskSummary, Recommendation, RecommendationSet,
    Alert, AlertSummary, InsightCard, Anomaly, OutcomeForecast,
    RiskPredictionResponse, CohortAnalysisResponse, TextReportResponse,
    BatchPredictionRequest, BatchPredictionResponse, GroupingRecommendation
)
from app.model import model_instance
from app.data_pipeline import data_pipeline
from app.risk_predictor import risk_predictor
from app.recommendation_engine import recommendation_engine
from app.alert_system import alert_system
from app.insights_generator import insights_generator

app = FastAPI(
    title="LBCA AI Monitoring System",
    description="AI-powered student performance monitoring and intervention system",
    version="1.0.0"
)

# ==================== BASIC ENDPOINTS ====================

@app.get("/")
def home():
    """Health check endpoint"""
    return {
        "message": "LBCA Performance API is running",
        "version": "1.0.0",
        "ai_features": "enabled"
    }

@app.post("/predict", response_model=PredictionOutput)
def predict(data: StudentInput):
    """Legacy prediction endpoint - basic model prediction"""
    try:
        prediction = model_instance.predict(data.features)
        return {"prediction": prediction}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ==================== RISK PREDICTION ENDPOINTS ====================

@app.post("/api/ai/predict-risk/", response_model=RiskAnalysis)
def predict_student_risk(data: StudentDataInput):
    """
    Predict risk for a single student
    
    Returns: Risk probability, confidence, early warnings, and risk factors
    """
    try:
        risk_analysis = risk_predictor.predict_student_risk(data.dict())
        return risk_analysis
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Risk prediction failed: {str(e)}")

@app.post("/api/ai/predict-risk/batch/", response_model=CohortRiskSummary)
def predict_cohort_risk(data: CohortDataInput):
    """
    Predict risk for multiple students (batch)
    
    Returns: Cohort summary with individual predictions
    """
    try:
        cohort_risk = risk_predictor.predict_cohort_risk(
            [s.dict() for s in data.students]
        )
        return cohort_risk
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Cohort risk prediction failed: {str(e)}")

# ==================== RECOMMENDATION ENDPOINTS ====================

@app.post("/api/ai/recommend-action/", response_model=RecommendationSet)
def get_recommendations(data: StudentDataInput):
    """
    Get intervention recommendations for a student
    
    Returns: Prioritized list of recommended interventions
    """
    try:
        risk_analysis = risk_predictor.predict_student_risk(data.dict())
        recommendations = recommendation_engine.generate_recommendations(risk_analysis)
        return {
            "student_id": data.student_id,
            "recommendations": recommendations
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Recommendation generation failed: {str(e)}")

@app.post("/api/ai/grouping-recommendation/", response_model=GroupingRecommendation)
def recommend_grouping(data: CohortDataInput):
    """
    Recommend peer study groups and mentoring pairings
    
    Returns: Optimized grouping recommendations
    """
    try:
        # Get risk data first
        cohort_risk = risk_predictor.predict_cohort_risk([s.dict() for s in data.students])
        
        # Generate grouping recommendations
        grouping = recommendation_engine.recommend_grouping(cohort_risk['predictions'])
        return grouping
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Grouping recommendation failed: {str(e)}")

# ==================== ALERT ENDPOINTS ====================

@app.post("/api/ai/check-alerts/", response_model=AlertSummary)
def check_cohort_alerts(data: CohortDataInput):
    """
    Check for alert conditions in a cohort
    
    Returns: All alerts (cohort-level and individual)
    """
    try:
        cohort_risk = risk_predictor.predict_cohort_risk([s.dict() for s in data.students])
        alerts = alert_system.check_cohort_alerts(cohort_risk)
        
        # Log alerts
        for alert in alerts['individual']:
            alert_system.log_alert(alert)
        
        return alerts
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Alert check failed: {str(e)}")

@app.get("/api/ai/alerts/student/{student_id}")
def get_student_alerts(student_id: str, limit: int = 10):
    """Get alert history for a specific student"""
    try:
        alerts = alert_system.get_student_alert_history(student_id, limit)
        return {
            "student_id": student_id,
            "alert_count": len(alerts),
            "alerts": alerts
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/ai/alerts/active")
def get_active_alerts(severity: Optional[str] = None):
    """Get all currently active alerts, optionally filtered by severity"""
    try:
        alerts = alert_system.get_active_alerts(severity)
        return {
            "total": len(alerts),
            "severity_filter": severity,
            "alerts": alerts
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ==================== INSIGHTS & ANALYSIS ENDPOINTS ====================

@app.post("/api/ai/insights/", response_model=CohortAnalysisResponse)
def get_dashboard_insights(data: CohortDataInput):
    """
    Get comprehensive dashboard insights for a cohort
    
    Returns: Insights, alerts, anomalies, and forecasts
    """
    try:
        # Get risk predictions
        cohort_risk = risk_predictor.predict_cohort_risk([s.dict() for s in data.students])
        
        # Generate insights
        insights = insights_generator.generate_dashboard_insights(cohort_risk)
        
        # Detect anomalies
        anomalies = insights_generator.detect_anomalies(cohort_risk['predictions'])
        
        # Generate forecast
        forecast = insights_generator.forecast_outcomes(cohort_risk['predictions'])
        
        # Check alerts
        alerts = alert_system.check_cohort_alerts(cohort_risk)
        
        return {
            "cohort_summary": cohort_risk,
            "insights": insights,
            "alerts": alerts,
            "anomalies": anomalies,
            "forecast": forecast
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Insights generation failed: {str(e)}")

@app.post("/api/ai/anomalies/", response_model=List[Anomaly])
def detect_anomalies(data: CohortDataInput):
    """
    Detect unusual performance patterns in cohort
    
    Returns: List of detected anomalies
    """
    try:
        cohort_risk = risk_predictor.predict_cohort_risk([s.dict() for s in data.students])
        anomalies = insights_generator.detect_anomalies(cohort_risk['predictions'])
        return anomalies
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Anomaly detection failed: {str(e)}")

@app.post("/api/ai/forecast/", response_model=OutcomeForecast)
def forecast_outcomes(data: CohortDataInput):
    """
    Forecast end-of-quarter outcomes
    
    Returns: Predicted graduation rates and pass/fail distribution
    """
    try:
        cohort_risk = risk_predictor.predict_cohort_risk([s.dict() for s in data.students])
        forecast = insights_generator.forecast_outcomes(cohort_risk['predictions'])
        return forecast
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Forecast generation failed: {str(e)}")

# ==================== REPORTING ENDPOINTS ====================

@app.post("/api/ai/report/text")
def generate_text_report(data: CohortDataInput, previous_data: Optional[CohortDataInput] = None):
    """
    Generate human-readable text report
    
    Returns: Formatted text report for email/PDF
    """
    try:
        cohort_risk = risk_predictor.predict_cohort_risk([s.dict() for s in data.students])
        
        previous_cohort = None
        if previous_data:
            previous_cohort = risk_predictor.predict_cohort_risk([s.dict() for s in previous_data.students])
        
        report = insights_generator.generate_text_report(cohort_risk, previous_cohort)
        
        return {
            "report": report,
            "generated_at": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Report generation failed: {str(e)}")

# ==================== DATA ANALYSIS ENDPOINTS ====================

@app.post("/api/ai/analyze-pattern/")
def analyze_patterns(data: CohortDataInput):
    """
    Analyze patterns in cohort performance
    
    Returns: Pattern analysis and insights
    """
    try:
        cohort_risk = risk_predictor.predict_cohort_risk([s.dict() for s in data.students])
        
        # Analyze patterns
        patterns = {
            'pace_declining_count': len([p for p in cohort_risk['predictions'] 
                                        if p['trends']['pace_direction'] == 'declining']),
            'pace_improving_count': len([p for p in cohort_risk['predictions'] 
                                        if p['trends']['pace_direction'] == 'improving']),
            'attendance_issues': len([p for p in cohort_risk['predictions'] 
                                     if p['trends']['attendance_info']['risk_level'] in ['medium', 'high']]),
            'subject_struggles': {},
        }
        
        # Track subject struggles
        for student in cohort_risk['predictions']:
            for subject in student['trends']['declining_subjects']:
                patterns['subject_struggles'][subject] = patterns['subject_struggles'].get(subject, 0) + 1
        
        return {
            "cohort_id": data.cohort_id,
            "total_students": cohort_risk['total_students'],
            "patterns": patterns,
            "recommendations": "Focus on students with declining PACE and attendance patterns"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Pattern analysis failed: {str(e)}")

# ==================== HEALTH & INFO ENDPOINTS ====================

@app.get("/api/ai/health")
def health_check():
    """Check AI system health"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "modules": {
            "data_pipeline": "active",
            "risk_predictor": "active",
            "recommendation_engine": "active",
            "alert_system": "active",
            "insights_generator": "active"
        }
    }

@app.get("/api/ai/info")
def system_info():
    """Get AI system information"""
    return {
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