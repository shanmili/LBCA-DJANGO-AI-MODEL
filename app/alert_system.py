"""
Alert System - Auto-detect risk threshold breaches and generate alerts
"""
from typing import Dict, List
from datetime import datetime
from enum import Enum

class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"

class AlertSystem:
    """
    Monitor student risk and generate alerts for critical situations
    """
    
    def __init__(self):
        # Alert thresholds
        self.thresholds = {
            'risk_probability': 0.65,  # 65% risk = alert
            'confidence': 0.70,         # High confidence increases alert weight
            'pace_drop': 15,            # 15% drop in PACE = alert
            'attendance_drop': 15,      # 15% drop in attendance = alert
            'consecutive_absences': 2,  # 2+ consecutive = alert
            'subject_fail': 55,         # Below 55% = alert
        }
        
        self.alert_history = {}  # Track alerts per student
    
    def check_student_alerts(self, risk_analysis: Dict, previous_analysis: Dict = None) -> List[Dict]:
        """
        Check if student triggers any alerts based on risk analysis
        
        Returns: list of triggered alerts
        """
        alerts = []
        student_id = risk_analysis.get('student_id')
        
        # Critical risk alert
        if risk_analysis.get('risk_probability', 0) >= (self.thresholds['risk_probability'] * 100):
            alerts.append(self._create_alert(
                student_id,
                AlertSeverity.CRITICAL,
                'high_risk_detected',
                f"Student at {risk_analysis.get('risk_probability')}% risk of falling behind",
                risk_analysis
            ))
        
        # High confidence warning - model is confident in the prediction
        if (risk_analysis.get('risk_probability', 0) >= 50 and 
            risk_analysis.get('confidence', 0) >= (self.thresholds['confidence'] * 100)):
            alerts.append(self._create_alert(
                student_id,
                AlertSeverity.CRITICAL,
                'high_confidence_warning',
                f"Model is {risk_analysis.get('confidence')}% confident in high-risk prediction",
                risk_analysis
            ))
        
        # Check for early warning indicators
        for warning in risk_analysis.get('early_warnings', []):
            if warning.get('severity') == 'critical':
                alerts.append(self._create_alert(
                    student_id,
                    AlertSeverity.CRITICAL,
                    warning.get('type'),
                    warning.get('message'),
                    risk_analysis
                ))
            elif warning.get('severity') == 'high':
                alerts.append(self._create_alert(
                    student_id,
                    AlertSeverity.WARNING,
                    warning.get('type'),
                    warning.get('message'),
                    risk_analysis
                ))
        
        # Compare with previous analysis to detect changes
        if previous_analysis:
            alerts.extend(self._check_change_alerts(risk_analysis, previous_analysis))
        
        return alerts
    
    def check_cohort_alerts(self, cohort_risk: Dict) -> Dict:
        """
        Generate cohort-level alerts
        
        Input: output from risk_predictor.predict_cohort_risk()
        """
        alerts = {
            'cohort_level': [],
            'individual': []
        }
        
        high_risk_count = cohort_risk.get('high_risk_count', 0)
        total = cohort_risk.get('total_students', 1)
        high_risk_pct = (high_risk_count / total) * 100
        
        # Cohort-level alerts
        if high_risk_count > 0:
            alerts['cohort_level'].append({
                'severity': AlertSeverity.WARNING.value,
                'type': 'cohort_high_risk',
                'message': f"{high_risk_count} students ({high_risk_pct:.0f}%) at high risk",
                'timestamp': datetime.now().isoformat(),
                'actionable': True
            })
        
        if high_risk_pct > 30:
            alerts['cohort_level'].append({
                'severity': AlertSeverity.CRITICAL.value,
                'type': 'cohort_crisis',
                'message': f"High-risk percentage ({high_risk_pct:.0f}%) exceeds threshold - intervention needed",
                'timestamp': datetime.now().isoformat(),
                'actionable': True
            })
        
        # Individual student alerts
        for prediction in cohort_risk.get('predictions', []):
            student_alerts = self.check_student_alerts(prediction)
            alerts['individual'].extend(student_alerts)
        
        return {
            'total_alerts': len(alerts['cohort_level']) + len(alerts['individual']),
            'critical_count': len([a for a in alerts['cohort_level'] + alerts['individual'] 
                                  if a.get('severity') == AlertSeverity.CRITICAL.value]),
            'cohort_level': alerts['cohort_level'],
            'individual': alerts['individual']
        }
    
    def _create_alert(self, student_id: str, severity: AlertSeverity, 
                     alert_type: str, message: str, risk_analysis: Dict) -> Dict:
        """Create an alert object"""
        return {
            'student_id': student_id,
            'severity': severity.value,
            'type': alert_type,
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'risk_level': risk_analysis.get('risk_level'),
            'confidence': risk_analysis.get('confidence'),
            'actionable': True,
            'recommended_action': self._get_recommended_action(alert_type, risk_analysis)
        }
    
    def _check_change_alerts(self, current: Dict, previous: Dict) -> List[Dict]:
        """Detect changes in student status that warrant alerts"""
        alerts = []
        
        # Risk increased significantly
        risk_increase = (current.get('risk_probability', 0) - 
                        previous.get('risk_probability', 0))
        if risk_increase > 20:
            alerts.append({
                'student_id': current.get('student_id'),
                'severity': AlertSeverity.WARNING.value,
                'type': 'risk_increased',
                'message': f"Risk increased by {risk_increase:.0f}% since last check",
                'timestamp': datetime.now().isoformat(),
                'previous_risk': previous.get('risk_probability'),
                'current_risk': current.get('risk_probability'),
                'actionable': True
            })
        
        # Status changed from low/medium to high
        prev_level = previous.get('risk_level')
        curr_level = current.get('risk_level')
        if prev_level != 'high' and curr_level == 'high':
            alerts.append({
                'student_id': current.get('student_id'),
                'severity': AlertSeverity.CRITICAL.value,
                'type': 'status_escalated',
                'message': f"Risk status escalated from {prev_level} to {curr_level}",
                'timestamp': datetime.now().isoformat(),
                'actionable': True
            })
        
        return alerts
    
    def _get_recommended_action(self, alert_type: str, risk_analysis: Dict) -> str:
        """Get recommended action for alert type"""
        actions = {
            'high_risk_detected': 'Schedule intervention meeting with student and parents',
            'high_confidence_warning': 'Prioritize student for immediate support',
            'pace_critical': 'Review PACE completion blockers - provide extension if needed',
            'pace_declining': 'Increase monitoring and check-ins',
            'attendance_critical': 'Contact parents about attendance concerns',
            'attendance_concerning': 'Monitor attendance trend closely',
            'absences_pattern': 'Investigate reason for recent absences',
            'subject_decline': 'Arrange peer tutoring or subject review',
            'teacher_concern': 'Meet with teacher to understand specific concerns',
            'risk_increased': 'Assess what changed - prioritize immediate intervention',
            'status_escalated': 'Escalate to support team - student now high-risk'
        }
        
        return actions.get(alert_type, 'Monitor student closely and reassess')
    
    def log_alert(self, alert: Dict):
        """Log alert to history for tracking"""
        student_id = alert.get('student_id')
        if student_id not in self.alert_history:
            self.alert_history[student_id] = []
        
        self.alert_history[student_id].append({
            **alert,
            'logged_at': datetime.now().isoformat()
        })
    
    def get_student_alert_history(self, student_id: str, limit: int = 10) -> List[Dict]:
        """Get alert history for a student"""
        return self.alert_history.get(student_id, [])[-limit:]
    
    def get_active_alerts(self, severity: str = None) -> List[Dict]:
        """Get all active alerts, optionally filtered by severity"""
        all_alerts = []
        for alerts in self.alert_history.values():
            all_alerts.extend(alerts)
        
        if severity:
            all_alerts = [a for a in all_alerts if a.get('severity') == severity]
        
        # Return alerts from last 7 days (simulated)
        return sorted(all_alerts, key=lambda x: x.get('timestamp'), reverse=True)

# Global instance
alert_system = AlertSystem()
