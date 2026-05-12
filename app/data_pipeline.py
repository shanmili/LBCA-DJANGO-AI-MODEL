"""
Data Pipeline - Cleaning, normalizing, and preparing student data for AI processing
PACE-ONLY: Attendance tracking removed. All predictions are based solely on PACE completion.
"""
import numpy as np
from typing import Dict, List, Tuple


class DataPipeline:
    """Handle data preparation and feature engineering"""

    def __init__(self):
        self.feature_names = [
            'pace_completion_pct',
            'pace_trend_slope',
            'ontime_submissions',
            'late_submissions',
            'teacher_concern_flag',
        ]

    def calculate_pace_trend(self, historical_pace: List[float]) -> Tuple[float, str]:
        """Calculate PACE completion trend"""
        if len(historical_pace) < 2:
            return 0.0, 'stable'

        recent = np.array(historical_pace[-4:])  # Last 4 records
        trend = np.polyfit(range(len(recent)), recent, 1)[0]

        if trend < -5:
            return trend, 'declining'
        elif trend > 5:
            return trend, 'improving'
        else:
            return trend, 'stable'

    def detect_score_decline(self, test_scores: Dict[str, List[float]]) -> List[str]:
        """Detect subjects with declining performance"""
        declining_subjects = []

        for subject, scores in test_scores.items():
            if len(scores) >= 2:
                recent_scores = np.array(scores[-3:])
                if len(recent_scores) >= 2:
                    decline = recent_scores[-1] - recent_scores[-2]
                    if decline < -10:  # 10+ point drop
                        declining_subjects.append(subject)

        return declining_subjects

    def normalize_features(self, features: Dict[str, float]) -> np.ndarray:
        """
        Normalize features to 0-1 range for model input.
        PACE-ONLY: attendance fields are replaced with zeros so the existing
        10-feature model still receives a valid 10-element vector.
        """
        normalized = np.array([
            min(features.get('pace_completion_pct', 0) / 100, 1.0),
            0.0,  # attendance_pct — not tracked, neutral placeholder
            min(features.get('math_score', 0) / 100, 1.0),
            min(features.get('english_score', 0) / 100, 1.0),
            min(features.get('science_score', 0) / 100, 1.0),
            0.0,  # absences_count — not tracked, neutral placeholder
            0.0,  # late_arrivals   — not tracked, neutral placeholder
            min(features.get('ontime_submissions', 0) / 20, 1.0),
            max(1 - (features.get('late_submissions', 0) / 10), 0),
            float(features.get('teacher_concern_flag', 0))
        ])

        return normalized

    def prepare_student_data(self, student_data: Dict) -> Dict:
        """
        Prepare complete student data for prediction.

        Input format (pace-only):
        {
            'student_id': 'S001',
            'current_week': 10,
            'pace_history': [45, 50, 55, ...],   # PACE % per record (required)
            'attendance_history': [],              # ignored — not tracked
            'test_scores': {'SubjectName': [70, 72, 68], ...},
            'absences_current': 0,                # ignored
            'late_arrivals_current': 0,           # ignored
            'submissions': {'ontime': 15, 'late': 2},
            'teacher_notes': ''
        }
        """
        student_id = student_data.get('student_id', 'Unknown')

        # ── PACE trend ──────────────────────────────────────────────────────────
        pace_history = student_data.get('pace_history', [])
        pace_trend, pace_direction = self.calculate_pace_trend(pace_history)
        current_pace = pace_history[-1] if pace_history else 0

        # ── Subject score trends (optional — pace_percent used as proxy) ────────
        test_scores = student_data.get('test_scores', {})
        declining_subjects = self.detect_score_decline(test_scores)

        # Pull subject scores if provided, otherwise default to current_pace
        # (frontend maps pace_percent into test_scores by subject)
        def last_score(subject):
            scores = test_scores.get(subject, [])
            return scores[-1] if scores else current_pace

        features_dict = {
            'pace_completion_pct': current_pace,
            # attendance intentionally omitted — set to neutral 100 so it
            # never inflates risk scores
            'attendance_pct': 100,
            'math_score': last_score('Math') if test_scores else current_pace,
            'english_score': last_score('English') if test_scores else current_pace,
            'science_score': last_score('Science') if test_scores else current_pace,
            'absences_count': 0,
            'late_arrivals': 0,
            'ontime_submissions': student_data.get('submissions', {}).get('ontime', 0),
            'late_submissions': student_data.get('submissions', {}).get('late', 0),
            'teacher_concern_flag': 1.0 if any(
                word in student_data.get('teacher_notes', '').lower()
                for word in ['struggle', 'concern', 'behind', 'issue', 'problem']
            ) else 0.0,
        }

        normalized_features = self.normalize_features(features_dict)

        return {
            'student_id': student_id,
            'features_dict': features_dict,
            'normalized_features': normalized_features,
            'trends': {
                'pace_trend': pace_trend,
                'pace_direction': pace_direction,
                # Neutral attendance info so downstream code doesn't crash
                'attendance_info': {'trend': 'not_tracked', 'risk_level': 'low', 'avg': 100},
                'declining_subjects': declining_subjects,
            },
        }


# Global instance
data_pipeline = DataPipeline()