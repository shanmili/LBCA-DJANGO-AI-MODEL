"""
Risk Predictor - Predict student risk with confidence scores and early warning indicators
"""
import numpy as np
from typing import Dict, Tuple
from app.model import model_instance
from app.data_pipeline import data_pipeline

class RiskPredictor:
    """
    Predict student dropout/performance risk with detailed analysis
    """
    
    def __init__(self):
        self.risk_thresholds = {
            'low': (0, 0.3),
            'medium': (0.3, 0.65),
            'high': (0.65, 1.0)
        }
        
    def predict_student_risk(self, student_data: Dict) -> Dict:
        """
        Predict risk for a single student
        
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
        # Prepare data
        prepared = data_pipeline.prepare_student_data(student_data)
        features = prepared['normalized_features']
        trends = prepared['trends']
        features_dict = prepared['features_dict']
        
        # Get base prediction from model
        try:
            raw_prediction = model_instance.predict(features.tolist())
            # Normalize to probability (0-1)
            if isinstance(raw_prediction, list):
                risk_prob = float(raw_prediction[0]) if raw_prediction else 0.5
            else:
                risk_prob = float(raw_prediction)
            
            # Clamp to 0-1 range
            risk_prob = max(0, min(1, risk_prob))
        except:
            risk_prob = 0.5  # Default to medium risk if prediction fails
        
        # Calculate confidence based on data consistency and warning signals
        confidence = self._calculate_confidence(prepared, risk_prob)
        
        # Identify early warning indicators
        early_warnings = self._identify_early_warnings(prepared, features_dict)
        
        # Identify risk factors and positive factors
        risk_factors = self._identify_risk_factors(prepared, features_dict)
        positive_factors = self._identify_positive_factors(prepared, features_dict)
        
        # Predict approximate drop-off week if high risk
        drop_week = self._predict_drop_week(prepared) if risk_prob > 0.65 else None
        
        # Determine risk level
        risk_level = self._get_risk_level(risk_prob)
        
        return {
            'student_id': prepared['student_id'],
            'risk_probability': round(risk_prob * 100, 1),
            'risk_level': risk_level,
            'confidence': round(confidence * 100, 1),
            'early_warnings': early_warnings,
            'predicted_drop_week': drop_week,
            'risk_factors': risk_factors,
            'positive_factors': positive_factors,
            'trends': trends
        }
    
    def predict_cohort_risk(self, students_data: list) -> Dict:
        """
        Predict risk for multiple students
        
        Returns summary statistics and individual predictions
        """
        predictions = [self.predict_student_risk(student) for student in students_data]
        
        risk_distribution = {
            'low': len([p for p in predictions if p['risk_level'] == 'low']),
            'medium': len([p for p in predictions if p['risk_level'] == 'medium']),
            'high': len([p for p in predictions if p['risk_level'] == 'high'])
        }
        
        return {
            'total_students': len(predictions),
            'risk_distribution': risk_distribution,
            'high_risk_count': risk_distribution['high'],
            'average_risk': round(np.mean([p['risk_probability'] for p in predictions]), 1),
            'average_confidence': round(np.mean([p['confidence'] for p in predictions]), 1),
            'predictions': predictions,
            'critical_students': [p for p in predictions if p['risk_level'] == 'high']
        }
    
    def _calculate_confidence(self, prepared: Dict, risk_prob: float) -> float:
        """Calculate confidence in the prediction"""
        features_dict = prepared['features_dict']
        trends = prepared['trends']
        
        confidence = 0.5  # Base confidence
        
        # Increase confidence with consistent warning signs
        warning_count = 0
        
        if features_dict['pace_completion_pct'] < 60:
            warning_count += 1
        if features_dict['attendance_pct'] < 80:
            warning_count += 1
        if features_dict['absences_count'] > 2:
            warning_count += 1
        if features_dict['late_submissions'] > 3:
            warning_count += 1
        if features_dict['teacher_concern_flag'] > 0.5:
            warning_count += 1
        if trends['pace_direction'] == 'declining':
            warning_count += 1
        
        # Multiple consistent warnings increase confidence
        confidence += min(warning_count * 0.08, 0.4)
        
        return max(0, min(1, confidence))
    
    def _identify_early_warnings(self, prepared: Dict, features_dict: Dict) -> list:
        """Identify early warning indicators"""
        warnings = []
        features_dict = prepared['features_dict']
        trends = prepared['trends']
        
        # PACE warning
        if features_dict['pace_completion_pct'] < 50:
            warnings.append({
                'type': 'pace_critical',
                'message': f"PACE completion critically low: {features_dict['pace_completion_pct']}%",
                'severity': 'critical'
            })
        elif features_dict['pace_completion_pct'] < 70:
            warnings.append({
                'type': 'pace_low',
                'message': f"PACE completion below target: {features_dict['pace_completion_pct']}%",
                'severity': 'high'
            })
        
        # Pace trend warning
        if trends['pace_direction'] == 'declining':
            warnings.append({
                'type': 'pace_declining',
                'message': f"PACE completion trending downward ({trends['pace_trend']:.1f}% per week)",
                'severity': 'high'
            })
        
        # Attendance warning
        if features_dict['attendance_pct'] < 75:
            warnings.append({
                'type': 'attendance_critical',
                'message': f"Attendance critically low: {features_dict['attendance_pct']}%",
                'severity': 'critical'
            })
        elif trends['attendance_info']['risk_level'] == 'medium':
            warnings.append({
                'type': 'attendance_concerning',
                'message': f"Attendance concerning: {trends['attendance_info']['avg']:.0f}%",
                'severity': 'medium'
            })
        
        # Absence pattern warning
        if features_dict['absences_count'] >= 3:
            warnings.append({
                'type': 'absences_pattern',
                'message': f"Multiple recent absences: {int(features_dict['absences_count'])} in last 2 weeks",
                'severity': 'high'
            })
        
        # Subject struggle warning
        if trends['declining_subjects']:
            subjects = ', '.join(trends['declining_subjects'])
            warnings.append({
                'type': 'subject_decline',
                'message': f"Declining scores in: {subjects}",
                'severity': 'medium'
            })
        
        # Teacher concern
        if features_dict['teacher_concern_flag'] > 0.5:
            warnings.append({
                'type': 'teacher_concern',
                'message': "Teacher flagged behavioral or academic concerns",
                'severity': 'high'
            })
        
        return warnings
    
    def _identify_risk_factors(self, prepared: Dict, features_dict: Dict) -> list:
        """Identify factors contributing to risk"""
        factors = []
        trends = prepared['trends']
        
        if features_dict['pace_completion_pct'] < 70:
            factors.append(f"Low PACE completion: {features_dict['pace_completion_pct']}%")
        if features_dict['attendance_pct'] < 85:
            factors.append(f"Below-target attendance: {features_dict['attendance_pct']}%")
        if features_dict['math_score'] < 70:
            factors.append(f"Math proficiency concerns: {features_dict['math_score']}%")
        if features_dict['english_score'] < 70:
            factors.append(f"English proficiency concerns: {features_dict['english_score']}%")
        if features_dict['absences_count'] > 1:
            factors.append(f"Recent absences: {int(features_dict['absences_count'])} instances")
        if features_dict['late_submissions'] > 2:
            factors.append(f"Submission delays: {int(features_dict['late_submissions'])} late submissions")
        if trends['pace_direction'] == 'declining':
            factors.append("PACE completion declining trend")
        if features_dict['teacher_concern_flag'] > 0.5:
            factors.append("Teacher reported concerns")
        
        return factors
    
    def _identify_positive_factors(self, prepared: Dict, features_dict: Dict) -> list:
        """Identify positive factors supporting student success"""
        factors = []
        
        if features_dict['pace_completion_pct'] > 80:
            factors.append(f"Strong PACE completion: {features_dict['pace_completion_pct']}%")
        if features_dict['attendance_pct'] > 90:
            factors.append(f"Excellent attendance: {features_dict['attendance_pct']}%")
        if features_dict['math_score'] > 80:
            factors.append(f"Strong math performance: {features_dict['math_score']}%")
        if features_dict['english_score'] > 80:
            factors.append(f"Strong English performance: {features_dict['english_score']}%")
        if features_dict['science_score'] > 80:
            factors.append(f"Strong science performance: {features_dict['science_score']}%")
        if features_dict['absences_count'] < 1:
            factors.append("Consistent attendance - no recent absences")
        if features_dict['ontime_submissions'] > 10:
            factors.append(f"Consistent submission: {int(features_dict['ontime_submissions'])} on-time submissions")
        
        return factors
    
    def _predict_drop_week(self, prepared: Dict) -> int:
        """Estimate which week student might drop off"""
        trends = prepared['trends']
        pace_trend = trends['pace_trend']
        
        # If declining at -5% per week and currently at 50%, ~10 weeks until 0%
        if pace_trend < -5:
            weeks_remaining = max(2, int(-50 / pace_trend))
            return min(weeks_remaining, 12)  # Cap at 12 weeks
        
        return None
    
    def _get_risk_level(self, probability: float) -> str:
        """Categorize risk probability into level"""
        if probability < 0.3:
            return 'low'
        elif probability < 0.65:
            return 'medium'
        else:
            return 'high'

# Global instance
risk_predictor = RiskPredictor()
