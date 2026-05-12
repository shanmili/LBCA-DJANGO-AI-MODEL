"""
LBCA AI Monitoring System — PACE-only build
CORS is configured here for local dev. Add ALLOWED_ORIGINS env var on Render
when the frontend is deployed.
"""
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from datetime import datetime

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
    description="AI-powered student PACE monitoring and intervention system",
    version="1.0.0",
)

# ── CORS ──────────────────────────────────────────────────────────────────────
allowed_origins = [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:5177",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",
]

extra = os.getenv("ALLOWED_ORIGINS", "")
if extra:
    allowed_origins += [o.strip() for o in extra.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Health ────────────────────────────────────────────────────────────────────

@app.get("/")
def home():
    return {
        "message": "LBCA AI (PACE-only) is running",
        "version": "1.0.0",
        "ai_features": "enabled",
    }

@app.get("/api/ai/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "modules": {
            "data_pipeline": "active",
            "risk_predictor": "active",
            "recommendation_engine": "active",
            "alert_system": "active",
            "insights_generator": "active",
        },
    }

@app.get("/api/ai/info")
def system_info():
    return {
        "system": "LBCA AI Monitoring System",
        "version": "1.0.0",
        "tracking": "PACE only — attendance not tracked",
        "features": [
            "Student risk prediction based on PACE completion",
            "Early warning indicators (PACE & subject trends)",
            "Intervention recommendations",
            "Cohort-level analysis",
            "Automatic alert generation",
            "Dashboard insights and forecasting",
        ],
    }

# ── Risk Prediction ───────────────────────────────────────────────────────────

@app.post("/predict", response_model=PredictionOutput)
def predict(data: StudentInput):
    """Legacy endpoint — basic model prediction"""
    try:
        prediction = model_instance.predict(data.features)
        return {"prediction": prediction}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/ai/predict-risk/", response_model=RiskAnalysis)
def predict_student_risk(data: StudentDataInput):
    """Predict PACE-based risk for a single student."""
    try:
        return risk_predictor.predict_student_risk(data.dict())
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Risk prediction failed: {str(e)}")

@app.post("/api/ai/predict-risk/batch/", response_model=CohortRiskSummary)
def predict_cohort_risk(data: CohortDataInput):
    """Predict PACE-based risk for multiple students (batch)."""
    try:
        return risk_predictor.predict_cohort_risk([s.dict() for s in data.students])
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Cohort risk prediction failed: {str(e)}")

# ── Recommendations ───────────────────────────────────────────────────────────

@app.post("/api/ai/recommend-action/", response_model=RecommendationSet)
def get_recommendations(data: StudentDataInput):
    """Get intervention recommendations for a student based on PACE."""
    try:
        risk_analysis = risk_predictor.predict_student_risk(data.dict())
        recommendations = recommendation_engine.generate_recommendations(risk_analysis)
        return {"student_id": data.student_id, "recommendations": recommendations}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Recommendation generation failed: {str(e)}")

@app.post("/api/ai/grouping-recommendation/", response_model=GroupingRecommendation)
def recommend_grouping(data: CohortDataInput):
    """Recommend peer study groups based on PACE risk levels."""
    try:
        cohort_risk = risk_predictor.predict_cohort_risk([s.dict() for s in data.students])
        return recommendation_engine.recommend_grouping(cohort_risk["predictions"])
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Grouping recommendation failed: {str(e)}")

# ── Alerts ────────────────────────────────────────────────────────────────────

@app.post("/api/ai/check-alerts/", response_model=AlertSummary)
def check_cohort_alerts(data: CohortDataInput):
    """Check for PACE-based alert conditions in a cohort."""
    try:
        cohort_risk = risk_predictor.predict_cohort_risk([s.dict() for s in data.students])
        alerts = alert_system.check_cohort_alerts(cohort_risk)
        for alert in alerts["individual"]:
            alert_system.log_alert(alert)
        return alerts
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Alert check failed: {str(e)}")

@app.get("/api/ai/alerts/active")
def get_active_alerts(severity: Optional[str] = None):
    """Get all currently active PACE-based alerts, optionally filtered by severity."""
    try:
        alerts = alert_system.get_active_alerts(severity)
        return {"total": len(alerts), "severity_filter": severity, "alerts": alerts}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/ai/alerts/student/{student_id}")
def get_student_alerts(student_id: str, limit: int = 10):
    """Get alert history for a specific student."""
    try:
        alerts = alert_system.get_student_alert_history(student_id, limit)
        return {"student_id": student_id, "alert_count": len(alerts), "alerts": alerts}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ── Insights & Analysis ───────────────────────────────────────────────────────

@app.post("/api/ai/insights/", response_model=CohortAnalysisResponse)
def get_dashboard_insights(data: CohortDataInput):
    """Get comprehensive PACE-based dashboard insights for a cohort."""
    try:
        cohort_risk = risk_predictor.predict_cohort_risk([s.dict() for s in data.students])
        insights    = insights_generator.generate_dashboard_insights(cohort_risk)
        anomalies   = insights_generator.detect_anomalies(cohort_risk["predictions"])
        forecast    = insights_generator.forecast_outcomes(cohort_risk["predictions"])
        alerts      = alert_system.check_cohort_alerts(cohort_risk)

        return {
            "cohort_summary": cohort_risk,
            "insights":       insights,
            "alerts":         alerts,
            "anomalies":      anomalies,
            "forecast":       forecast,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Insights generation failed: {str(e)}")

@app.post("/api/ai/anomalies/", response_model=List[Anomaly])
def detect_anomalies(data: CohortDataInput):
    """Detect unusual PACE performance patterns in cohort."""
    try:
        cohort_risk = risk_predictor.predict_cohort_risk([s.dict() for s in data.students])
        return insights_generator.detect_anomalies(cohort_risk["predictions"])
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Anomaly detection failed: {str(e)}")

@app.post("/api/ai/forecast/", response_model=OutcomeForecast)
def forecast_outcomes(data: CohortDataInput):
    """Forecast end-of-quarter outcomes based on PACE data."""
    try:
        cohort_risk = risk_predictor.predict_cohort_risk([s.dict() for s in data.students])
        return insights_generator.forecast_outcomes(cohort_risk["predictions"])
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Forecast generation failed: {str(e)}")

@app.post("/api/ai/report/text")
def generate_text_report(data: CohortDataInput, previous_data: Optional[CohortDataInput] = None):
    """Generate human-readable PACE report."""
    try:
        cohort_risk = risk_predictor.predict_cohort_risk([s.dict() for s in data.students])
        previous_cohort = None
        if previous_data:
            previous_cohort = risk_predictor.predict_cohort_risk(
                [s.dict() for s in previous_data.students]
            )
        report = insights_generator.generate_text_report(cohort_risk, previous_cohort)
        return {"report": report, "generated_at": datetime.now().isoformat()}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Report generation failed: {str(e)}")

@app.post("/api/ai/analyze-pattern/")
def analyze_patterns(data: CohortDataInput):
    """Analyze PACE patterns in cohort performance."""
    try:
        cohort_risk = risk_predictor.predict_cohort_risk([s.dict() for s in data.students])
        predictions = cohort_risk["predictions"]

        patterns = {
            "pace_declining_count": len([
                p for p in predictions if p["trends"]["pace_direction"] == "declining"
            ]),
            "pace_improving_count": len([
                p for p in predictions if p["trends"]["pace_direction"] == "improving"
            ]),
            "subject_struggles": {},
        }

        for student in predictions:
            for subject in student["trends"]["declining_subjects"]:
                patterns["subject_struggles"][subject] = (
                    patterns["subject_struggles"].get(subject, 0) + 1
                )

        return {
            "cohort_id":       data.cohort_id,
            "total_students":  cohort_risk["total_students"],
            "patterns":        patterns,
            "recommendations": "Focus on students with declining PACE completion",
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Pattern analysis failed: {str(e)}")