"""
Recommendation Engine - Generate intervention recommendations based on student profile
"""
from typing import Dict, List
from enum import Enum

class InterventionType(Enum):
    """Types of interventions available"""
    TUTORING = "tutoring"
    PEER_STUDY = "peer_study"
    CHECK_IN = "check_in"
    PARENT_CONTACT = "parent_contact"
    CONTENT_REVIEW = "content_review"
    GROUPING = "grouping"
    TEACHER_SUPPORT = "teacher_support"
    PACE_EXTENSION = "pace_extension"

class RecommendationEngine:
    """
    Generate personalized intervention recommendations based on risk analysis
    """
    
    def __init__(self):
        self.interventions_db = {
            'math_struggle': {
                'type': InterventionType.TUTORING,
                'priority': 'high',
                'action': 'Schedule 1-on-1 tutoring session for Math concepts',
                'frequency': 'weekly'
            },
            'pace_critical': {
                'type': InterventionType.PACE_EXTENSION,
                'priority': 'critical',
                'action': 'Review PACE completion blockers - provide extension if needed',
                'frequency': 'immediate'
            },
            'attendance_low': {
                'type': InterventionType.PARENT_CONTACT,
                'priority': 'high',
                'action': 'Parent communication recommended - discuss attendance',
                'frequency': 'bi-weekly'
            },
            'declining_performance': {
                'type': InterventionType.CHECK_IN,
                'priority': 'high',
                'action': 'Increase check-in frequency - identify learning blockers',
                'frequency': 'weekly'
            },
            'peer_support': {
                'type': InterventionType.PEER_STUDY,
                'priority': 'medium',
                'action': 'Organize peer study group with similar-performing students',
                'frequency': 'bi-weekly'
            },
            'subject_review': {
                'type': InterventionType.CONTENT_REVIEW,
                'priority': 'medium',
                'action': 'Content review session for struggling subjects',
                'frequency': 'weekly'
            },
            'teacher_concern': {
                'type': InterventionType.TEACHER_SUPPORT,
                'priority': 'high',
                'action': 'Teacher provides behavioral/academic support',
                'frequency': 'as-needed'
            }
        }
    
    def generate_recommendations(self, risk_analysis: Dict) -> List[Dict]:
        """
        Generate prioritized recommendations based on risk analysis
        
        Input: output from risk_predictor.predict_student_risk()
        Output: sorted list of intervention recommendations
        """
        recommendations = []
        risk_factors = risk_analysis.get('risk_factors', [])
        warnings = risk_analysis.get('early_warnings', [])
        confidence = risk_analysis.get('confidence', 0)
        
        # Build recommendation set based on risk factors
        if any('PACE' in str(w) for w in risk_factors):
            rec = self._build_recommendation(
                'pace_critical' if any('critical' in str(w).lower() for w in warnings) else 'declining_performance',
                risk_analysis
            )
            if rec:
                recommendations.append(rec)
        
        if any('Math' in str(f) for f in risk_factors):
            rec = self._build_recommendation('math_struggle', risk_analysis)
            if rec:
                recommendations.append(rec)
        
        if any('Attendance' in str(f) for f in risk_factors):
            rec = self._build_recommendation('attendance_low', risk_analysis)
            if rec:
                recommendations.append(rec)
        
        if any('declining' in str(f).lower() or 'Declining' in str(f) for f in risk_factors):
            rec = self._build_recommendation('declining_performance', risk_analysis)
            if rec and rec not in recommendations:
                recommendations.append(rec)
        
        if any('Teacher' in str(f) or 'concern' in str(f).lower() for f in risk_factors):
            rec = self._build_recommendation('teacher_concern', risk_analysis)
            if rec:
                recommendations.append(rec)
        
        # Add peer support if there are enough similar peers (assume available)
        if len(risk_factors) >= 2:
            rec = self._build_recommendation('peer_support', risk_analysis)
            if rec:
                recommendations.append(rec)
        
        # Sort by priority and confidence
        priority_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        recommendations.sort(
            key=lambda x: (priority_order.get(x['priority'], 4), -x['confidence_score'])
        )
        
        # Limit to top 5 recommendations
        return recommendations[:5]
    
    def _build_recommendation(self, intervention_key: str, risk_analysis: Dict) -> Dict:
        """Build a single recommendation with context"""
        if intervention_key not in self.interventions_db:
            return None
        
        base = self.interventions_db[intervention_key]
        
        # Add context from risk analysis
        context = self._build_context(intervention_key, risk_analysis)
        
        return {
            'type': base['type'].value,
            'priority': base['priority'],
            'action': base['action'],
            'context': context,
            'frequency': base['frequency'],
            'confidence_score': risk_analysis.get('confidence', 50),
            'urgency': 'immediate' if base['priority'] in ['critical', 'high'] and risk_analysis.get('confidence', 0) > 70 else 'normal'
        }
    
    def _build_context(self, intervention_key: str, risk_analysis: Dict) -> str:
        """Add contextual information to recommendations"""
        risk_factors = risk_analysis.get('risk_factors', [])
        warnings = risk_analysis.get('early_warnings', [])
        
        context = ""
        
        if intervention_key == 'pace_critical':
            pace = next((f for f in risk_factors if 'PACE' in f), 'PACE completion')
            context = f"Student's {pace.lower()} - needs immediate intervention to prevent further decline"
        
        elif intervention_key == 'math_struggle':
            score = next((f for f in risk_factors if 'Math' in f or 'math' in f), 'Math score needs improvement')
            context = f"{score} - recommend targeted math tutoring"
        
        elif intervention_key == 'attendance_low':
            att = next((f for f in risk_factors if 'attendance' in f.lower()), 'Attendance is below target')
            context = f"{att} - discuss barriers with student and parents"
        
        elif intervention_key == 'declining_performance':
            declining = next((f for f in risk_factors if 'declining' in f.lower()), 'Performance is declining')
            context = f"Trend analysis shows {declining.lower()} - increase support and monitoring"
        
        elif intervention_key == 'peer_support':
            context = "Group with similar-performing students for collaborative learning"
        
        elif intervention_key == 'teacher_concern':
            context = "Teacher has flagged concerns - provide support and resources to address them"
        
        return context
    
    def recommend_grouping(self, students_risk_data: List[Dict]) -> Dict:
        """
        Recommend student groupings for peer study
        
        Input: list of risk predictions for a cohort
        Output: grouping recommendations
        """
        # Group students by performance level
        low_risk = [s for s in students_risk_data if s['risk_level'] == 'low']
        medium_risk = [s for s in students_risk_data if s['risk_level'] == 'medium']
        high_risk = [s for s in students_risk_data if s['risk_level'] == 'high']
        
        groupings = []
        
        # Create mixed-level study groups (mentor + learner model)
        peer_tutors = [s for s in low_risk if s['confidence'] > 75]  # High-confidence low-risk students
        struggling = [s for s in high_risk]
        
        for i, student in enumerate(struggling):
            if i < len(peer_tutors):
                groupings.append({
                    'group_name': f"Study Group {i+1}",
                    'mentor': peer_tutors[i]['student_id'],
                    'mentees': [student['student_id']],
                    'focus': student.get('risk_factors', [None])[0],
                    'frequency': 'twice weekly'
                })
        
        # Group remaining medium-risk students together
        for i in range(0, len(medium_risk), 3):
            group = medium_risk[i:i+3]
            if len(group) >= 2:
                groupings.append({
                    'group_name': f"Collaborative Group {len(groupings)+1}",
                    'members': [s['student_id'] for s in group],
                    'focus': 'Collaborative learning and peer support',
                    'frequency': 'weekly'
                })
        
        return {
            'total_groups': len(groupings),
            'groupings': groupings,
            'mentorship_opportunities': len(peer_tutors),
            'peer_tutors': [s['student_id'] for s in peer_tutors]
        }
    
    def recommend_teachers(self, student_risk: Dict, available_teachers: List[Dict]) -> Dict:
        """
        Recommend best-suited teachers for a student
        
        Input: student risk analysis, available teachers with specialties
        Output: ranked teacher recommendations
        """
        risk_factors = student_risk.get('risk_factors', [])
        
        teacher_scores = []
        
        for teacher in available_teachers:
            score = 0
            specialties = teacher.get('specialties', [])
            
            # Match subject expertise to student's struggles
            if any('Math' in f for f in risk_factors) and 'Mathematics' in specialties:
                score += 30
            if any('English' in f for f in risk_factors) and 'English' in specialties:
                score += 30
            if any('Science' in f for f in risk_factors) and 'Science' in specialties:
                score += 30
            
            # Prefer teachers with track record in intervention
            if teacher.get('intervention_success_rate', 0) > 0.75:
                score += 20
            
            # Students with attendance issues benefit from relationship-building teachers
            if any('Attendance' in f for f in risk_factors) and teacher.get('mentoring_focus') == True:
                score += 15
            
            if score > 0:
                teacher_scores.append({
                    'teacher_id': teacher.get('id'),
                    'teacher_name': teacher.get('name'),
                    'score': score,
                    'matching_specialties': [s for s in specialties if any(s in f for f in risk_factors)]
                })
        
        # Sort by score
        teacher_scores.sort(key=lambda x: x['score'], reverse=True)
        
        return {
            'student_id': student_risk.get('student_id'),
            'recommended_teachers': teacher_scores[:3],
            'primary_teacher': teacher_scores[0] if teacher_scores else None
        }

# Global instance
recommendation_engine = RecommendationEngine()
