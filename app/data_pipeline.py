"""
Data Pipeline - Cleaning, normalizing, and preparing student data for AI processing
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
from datetime import datetime, timedelta

class DataPipeline:
    """Handle data preparation and feature engineering"""
    
    def __init__(self):
        self.feature_names = [
            'pace_completion_pct',
            'attendance_pct',
            'math_score',
            'english_score', 
            'science_score',
            'absences_count',
            'late_arrivals',
            'ontime_submissions',
            'late_submissions',
            'teacher_concern_flag'
        ]
        
    def calculate_pace_trend(self, historical_pace: List[float]) -> Tuple[float, str]:
        """Calculate PACE completion trend"""
        if len(historical_pace) < 2:
            return 0.0, 'stable'
        
        recent = np.array(historical_pace[-4:])  # Last 4 weeks
        trend = np.polyfit(range(len(recent)), recent, 1)[0]
        
        if trend < -5:
            return trend, 'declining'
        elif trend > 5:
            return trend, 'improving'
        else:
            return trend, 'stable'
    
    def calculate_attendance_trend(self, weekly_attendance: List[float]) -> Dict:
        """Analyze attendance patterns"""
        if not weekly_attendance:
            return {'trend': 'unknown', 'risk_level': 'medium'}
        
        recent = weekly_attendance[-4:]
        avg_recent = np.mean(recent)
        
        if avg_recent < 70:
            return {'trend': 'poor', 'risk_level': 'high', 'avg': avg_recent}
        elif avg_recent < 85:
            return {'trend': 'concerning', 'risk_level': 'medium', 'avg': avg_recent}
        else:
            return {'trend': 'good', 'risk_level': 'low', 'avg': avg_recent}
    
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
        Normalize features to 0-1 range for model input
        Expected keys: pace_completion_pct, attendance_pct, math_score, 
                      english_score, science_score, absences_count, late_arrivals,
                      ontime_submissions, late_submissions, teacher_concern_flag
        """
        normalized = np.array([
            min(features.get('pace_completion_pct', 0) / 100, 1.0),
            min(features.get('attendance_pct', 0) / 100, 1.0),
            min(features.get('math_score', 0) / 100, 1.0),
            min(features.get('english_score', 0) / 100, 1.0),
            min(features.get('science_score', 0) / 100, 1.0),
            max(1 - (features.get('absences_count', 0) / 10), 0),  # Inverted: fewer absences = better
            max(1 - (features.get('late_arrivals', 0) / 10), 0),   # Inverted
            min(features.get('ontime_submissions', 0) / 20, 1.0),
            max(1 - (features.get('late_submissions', 0) / 10), 0), # Inverted
            float(features.get('teacher_concern_flag', 0))
        ])
        
        return normalized
    
    def prepare_student_data(self, student_data: Dict) -> Dict:
        """
        Prepare complete student data for prediction
        
        Input format:
        {
            'student_id': 'S001',
            'current_week': 10,
            'pace_history': [45, 50, 55, ...],
            'attendance_history': [90, 92, 88, ...],
            'test_scores': {'math': [70, 72, 68], 'english': [...], ...},
            'absences_current': 2,
            'late_arrivals_current': 1,
            'submissions': {'ontime': 15, 'late': 2},
            'teacher_notes': "Struggling with concepts"
        }
        """
        student_id = student_data.get('student_id', 'Unknown')
        
        # Calculate trends
        pace_trend, pace_direction = self.calculate_pace_trend(
            student_data.get('pace_history', [50])
        )
        
        attendance_info = self.calculate_attendance_trend(
            student_data.get('attendance_history', [80])
        )
        
        declining_subjects = self.detect_score_decline(
            student_data.get('test_scores', {})
        )
        
        # Current metrics
        current_pace = student_data.get('pace_history', [0])[-1] if student_data.get('pace_history') else 0
        current_attendance = student_data.get('attendance_history', [0])[-1] if student_data.get('attendance_history') else 0
        
        test_scores = student_data.get('test_scores', {})
        current_scores = {
            'math': test_scores.get('math', [0])[-1] if test_scores.get('math') else 0,
            'english': test_scores.get('english', [0])[-1] if test_scores.get('english') else 0,
            'science': test_scores.get('science', [0])[-1] if test_scores.get('science') else 0,
        }
        
        features_dict = {
            'pace_completion_pct': current_pace,
            'attendance_pct': current_attendance,
            'math_score': current_scores['math'],
            'english_score': current_scores['english'],
            'science_score': current_scores['science'],
            'absences_count': student_data.get('absences_current', 0),
            'late_arrivals': student_data.get('late_arrivals_current', 0),
            'ontime_submissions': student_data.get('submissions', {}).get('ontime', 0),
            'late_submissions': student_data.get('submissions', {}).get('late', 0),
            'teacher_concern_flag': 1.0 if any(word in student_data.get('teacher_notes', '').lower() 
                                               for word in ['struggle', 'concern', 'behind', 'issue', 'problem']) else 0.0
        }
        
        normalized_features = self.normalize_features(features_dict)
        
        return {
            'student_id': student_id,
            'features_dict': features_dict,
            'normalized_features': normalized_features,
            'trends': {
                'pace_trend': pace_trend,
                'pace_direction': pace_direction,
                'attendance_info': attendance_info,
                'declining_subjects': declining_subjects,
            }
        }

# Global instance
data_pipeline = DataPipeline()
