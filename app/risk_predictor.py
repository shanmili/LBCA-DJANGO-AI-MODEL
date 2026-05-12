"""
Risk Predictor - Predict student risk with confidence scores and early warning indicators
PACE-ONLY: Attendance-based warnings removed. Risk is driven entirely by PACE completion.
"""
import numpy as np
from typing import Dict, Tuple
from app.model import model_instance
from app.data_pipeline import data_pipeline


class RiskPredictor:
    """
    Predict student dropout/performance risk with detailed analysis.
    Only uses PACE data — no attendance.
    """

    def __init__(self):
        self.risk_thresholds = {
            'low':    (0,    0.3),
            'medium': (0.3,  0.65),
            'high':   (0.65, 1.0),
        }

    def predict_student_risk(self, student_data: Dict) -> Dict:
        """
        Predict risk for a single student.

        Returns: {
            'student_id': str,
            'risk_probability': float (0-100),
            'risk_level': str (low/medium/high),
            'confidence': float (0-100),
            'early_warnings': list,
            'predicted_drop_week': int or None,
            'risk_factors': list,
            'positive_factors': list
        }
        """
        prepared       = data_pipeline.prepare_student_data(student_data)
        features       = prepared['normalized_features']
        trends         = prepared['trends']
        features_dict  = prepared['features_dict']

        # ── Base model prediction ────────────────────────────────────────────
        try:
            raw_prediction = model_instance.predict(features.tolist())
            risk_prob = float(raw_prediction[0]) if isinstance(raw_prediction, list) else float(raw_prediction)
            risk_prob = max(0, min(1, risk_prob))
        except Exception:
            # If model fails, derive risk directly from pace (no attendance bias)
            pace = features_dict['pace_completion_pct']
            risk_prob = 0.8 if pace < 50 else 0.5 if pace < 70 else 0.2

        # ── Override using PACE if model was trained with attendance features ─
        # Re-weight: attendance columns are neutral (100 %) so the raw model
        # output may under-predict. Adjust based on pace directly.
        pace = features_dict['pace_completion_pct']
        if pace < 50:
            risk_prob = max(risk_prob, 0.70)
        elif pace < 70:
            risk_prob = max(risk_prob, 0.40)
        elif pace >= 85:
            risk_prob = min(risk_prob, 0.30)

        # ── Derived outputs ──────────────────────────────────────────────────
        confidence      = self._calculate_confidence(prepared, risk_prob)
        early_warnings  = self._identify_early_warnings(prepared, features_dict)
        risk_factors    = self._identify_risk_factors(prepared, features_dict)
        positive_factors = self._identify_positive_factors(prepared, features_dict)
        drop_week       = self._predict_drop_week(prepared) if risk_prob > 0.65 else None
        risk_level      = self._get_risk_level(risk_prob)

        return {
            'student_id':        prepared['student_id'],
            'risk_probability':  round(risk_prob * 100, 1),
            'risk_level':        risk_level,
            'confidence':        round(confidence * 100, 1),
            'early_warnings':    early_warnings,
            'predicted_drop_week': drop_week,
            'risk_factors':      risk_factors,
            'positive_factors':  positive_factors,
            'trends':            trends,
        }

    def predict_cohort_risk(self, students_data: list) -> Dict:
        """Predict risk for multiple students and return cohort summary."""
        predictions = [self.predict_student_risk(s) for s in students_data]

        risk_distribution = {
            'low':    len([p for p in predictions if p['risk_level'] == 'low']),
            'medium': len([p for p in predictions if p['risk_level'] == 'medium']),
            'high':   len([p for p in predictions if p['risk_level'] == 'high']),
        }

        return {
            'total_students':    len(predictions),
            'risk_distribution': risk_distribution,
            'high_risk_count':   risk_distribution['high'],
            'average_risk':      round(np.mean([p['risk_probability'] for p in predictions]), 1),
            'average_confidence': round(np.mean([p['confidence'] for p in predictions]), 1),
            'predictions':       predictions,
            'critical_students': [p for p in predictions if p['risk_level'] == 'high'],
        }

    # ── internal helpers ─────────────────────────────────────────────────────

    def _calculate_confidence(self, prepared: Dict, risk_prob: float) -> float:
        """Confidence based solely on PACE signals (no attendance)."""
        features_dict = prepared['features_dict']
        trends        = prepared['trends']

        confidence = 0.5  # base

        warning_count = 0
        if features_dict['pace_completion_pct'] < 60:
            warning_count += 2          # strong pace signal
        elif features_dict['pace_completion_pct'] < 75:
            warning_count += 1
        if features_dict['late_submissions'] > 3:
            warning_count += 1
        if features_dict['teacher_concern_flag'] > 0.5:
            warning_count += 1
        if trends['pace_direction'] == 'declining':
            warning_count += 1

        confidence += min(warning_count * 0.08, 0.4)
        return max(0, min(1, confidence))

    def _identify_early_warnings(self, prepared: Dict, features_dict: Dict) -> list:
        """PACE-only early warnings — no attendance."""
        warnings = []
        trends   = prepared['trends']
        pace     = features_dict['pace_completion_pct']

        if pace < 50:
            warnings.append({
                'type':     'pace_critical',
                'message':  f"PACE completion critically low: {pace:.0f}%",
                'severity': 'critical',
            })
        elif pace < 70:
            warnings.append({
                'type':     'pace_low',
                'message':  f"PACE completion below target: {pace:.0f}%",
                'severity': 'high',
            })

        if trends['pace_direction'] == 'declining':
            warnings.append({
                'type':     'pace_declining',
                'message':  f"PACE trending downward ({trends['pace_trend']:.1f}% per record)",
                'severity': 'high',
            })

        if trends['declining_subjects']:
            subjects = ', '.join(trends['declining_subjects'])
            warnings.append({
                'type':     'subject_decline',
                'message':  f"Declining scores in: {subjects}",
                'severity': 'medium',
            })

        if features_dict['teacher_concern_flag'] > 0.5:
            warnings.append({
                'type':     'teacher_concern',
                'message':  "Teacher flagged academic or behavioral concerns",
                'severity': 'high',
            })

        return warnings

    def _identify_risk_factors(self, prepared: Dict, features_dict: Dict) -> list:
        """PACE-only risk factors."""
        factors = []
        trends  = prepared['trends']
        pace    = features_dict['pace_completion_pct']

        if pace < 70:
            factors.append(f"Low PACE completion: {pace:.0f}%")
        if features_dict['late_submissions'] > 2:
            factors.append(f"Submission delays: {int(features_dict['late_submissions'])} late submissions")
        if trends['pace_direction'] == 'declining':
            factors.append("PACE completion declining trend")
        if features_dict['teacher_concern_flag'] > 0.5:
            factors.append("Teacher reported concerns")
        if trends['declining_subjects']:
            factors.append(f"Declining scores in: {', '.join(trends['declining_subjects'])}")

        return factors

    def _identify_positive_factors(self, prepared: Dict, features_dict: Dict) -> list:
        """PACE-only positive factors."""
        factors = []
        pace    = features_dict['pace_completion_pct']

        if pace >= 90:
            factors.append(f"Excellent PACE completion: {pace:.0f}%")
        elif pace >= 80:
            factors.append(f"Strong PACE completion: {pace:.0f}%")
        if features_dict['ontime_submissions'] > 10:
            factors.append(f"Consistent on-time submissions: {int(features_dict['ontime_submissions'])}")

        return factors

    def _predict_drop_week(self, prepared: Dict) -> int:
        """Estimate which week student might drop off based on PACE trend."""
        trends     = prepared['trends']
        pace_trend = trends['pace_trend']
        pace       = prepared['features_dict']['pace_completion_pct']

        if pace_trend < -5:
            weeks_remaining = max(2, int((pace / abs(pace_trend))))
            return min(weeks_remaining, 12)

        return None

    def _get_risk_level(self, probability: float) -> str:
        if probability < 0.3:
            return 'low'
        elif probability < 0.65:
            return 'medium'
        else:
            return 'high'


# Global instance
risk_predictor = RiskPredictor()