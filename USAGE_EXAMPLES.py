"""
LBCA AI Monitoring System - Complete Usage Examples

This file demonstrates how to use all AI features with practical examples.
Use these as templates for your own integration.
"""

import requests
import json
from datetime import datetime

# API Base URL
BASE_URL = "http://localhost:8000"

# ============================================================================
# EXAMPLE 1: Simple Risk Check for One Student
# ============================================================================

def example_1_single_student_risk():
    """Check risk for a single student"""
    
    student_data = {
        "student_id": "S001",
        "pace_history": [45, 50, 55, 60, 58, 56, 54, 52],
        "attendance_history": [90, 92, 88, 85, 80, 78, 75, 72],
        "test_scores": {
            "math": [70, 72, 68, 65, 62],
            "english": [75, 76, 74, 72],
            "science": [80, 82, 81, 80]
        },
        "absences_current": 2,
        "late_arrivals_current": 1,
        "submissions": {"ontime": 15, "late": 2},
        "teacher_notes": "Struggling with math, showing promise in English"
    }
    
    # Get risk prediction
    response = requests.post(
        f"{BASE_URL}/api/ai/predict-risk/",
        json=student_data
    )
    
    if response.status_code == 200:
        result = response.json()
        
        print("=" * 60)
        print(f"STUDENT: {result['student_id']}")
        print("=" * 60)
        print(f"Risk Level: {result['risk_level'].upper()}")
        print(f"Risk Probability: {result['risk_probability']}%")
        print(f"Confidence: {result['confidence']}%")
        
        if result['early_warnings']:
            print("\n⚠️  EARLY WARNINGS:")
            for warning in result['early_warnings']:
                print(f"  - [{warning['severity'].upper()}] {warning['message']}")
        
        if result['risk_factors']:
            print("\n❌ RISK FACTORS:")
            for factor in result['risk_factors']:
                print(f"  - {factor}")
        
        if result['positive_factors']:
            print("\n✅ POSITIVE FACTORS:")
            for factor in result['positive_factors']:
                print(f"  - {factor}")
    
    return response.json()


# ============================================================================
# EXAMPLE 2: Cohort Risk Analysis
# ============================================================================

def example_2_cohort_analysis():
    """Analyze risk for entire cohort"""
    
    # Create sample cohort data
    cohort_data = {
        "cohort_id": "Section A - Week 10",
        "students": [
            {
                "student_id": f"S{i:03d}",
                "pace_history": [45 + i*3, 50 + i*3, 55 + i*3, 60 + i*3, 58 + i*3],
                "attendance_history": [85 + i, 87 + i, 85 + i, 88 + i, 86 + i],
                "test_scores": {
                    "math": [65 + i*2, 68 + i*2, 70 + i*2],
                    "english": [70 + i, 72 + i, 74 + i]
                },
                "absences_current": max(0, 3 - i),
                "late_arrivals_current": 0,
                "submissions": {"ontime": 15 + i, "late": max(0, 5 - i)},
                "teacher_notes": ""
            }
            for i in range(10)  # 10 students
        ]
    }
    
    # Get cohort risk summary
    response = requests.post(
        f"{BASE_URL}/api/ai/predict-risk/batch/",
        json=cohort_data
    )
    
    if response.status_code == 200:
        result = response.json()
        
        print("\n" + "=" * 60)
        print("COHORT RISK ANALYSIS")
        print("=" * 60)
        print(f"Total Students: {result['total_students']}")
        print(f"\nRisk Distribution:")
        print(f"  Low Risk: {result['risk_distribution']['low']}")
        print(f"  Medium Risk: {result['risk_distribution']['medium']}")
        print(f"  High Risk: {result['risk_distribution']['high']}")
        print(f"\nAverage Risk: {result['average_risk']}%")
        print(f"Prediction Confidence: {result['average_confidence']}%")
        
        if result['critical_students']:
            print(f"\n🚨 CRITICAL STUDENTS ({len(result['critical_students'])}):")
            for student in result['critical_students'][:5]:
                print(f"  - {student['student_id']}: {student['risk_probability']}% risk")
    
    return response.json()


# ============================================================================
# EXAMPLE 3: Get Recommendations for a Student
# ============================================================================

def example_3_recommendations():
    """Get intervention recommendations"""
    
    student_data = {
        "student_id": "S001",
        "pace_history": [45, 50, 55, 60, 58, 56, 54, 52],
        "attendance_history": [90, 92, 88, 85, 80, 78, 75, 72],
        "test_scores": {
            "math": [70, 72, 68, 65, 62],
            "english": [75, 76, 74, 72]
        },
        "absences_current": 2,
        "late_arrivals_current": 1,
        "submissions": {"ontime": 15, "late": 2},
        "teacher_notes": "Struggling with math"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/ai/recommend-action/",
        json=student_data
    )
    
    if response.status_code == 200:
        result = response.json()
        
        print("\n" + "=" * 60)
        print(f"RECOMMENDATIONS FOR {result['student_id']}")
        print("=" * 60)
        
        for i, rec in enumerate(result['recommendations'], 1):
            priority_emoji = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}
            emoji = priority_emoji.get(rec['priority'], "⚪")
            
            print(f"\n{i}. {emoji} {rec['type'].upper()} [{rec['priority'].upper()}]")
            print(f"   Action: {rec['action']}")
            print(f"   Context: {rec['context']}")
            print(f"   Frequency: {rec['frequency']}")
            print(f"   Urgency: {rec['urgency']}")
    
    return response.json()


# ============================================================================
# EXAMPLE 4: Daily Alert Check
# ============================================================================

def example_4_daily_alert_check():
    """Check for alerts in cohort"""
    
    cohort_data = {
        "cohort_id": "Section A",
        "students": [
            {
                "student_id": f"S{i:03d}",
                "pace_history": [45 + i*3 - (3 if i == 1 else 0), 50 + i*3, 55 + i*3],
                "attendance_history": [85, 85, 85, 85 if i != 2 else 70],
                "test_scores": {"math": [65 + i*2, 68 + i*2]},
                "absences_current": 0 if i != 3 else 3,
                "late_arrivals_current": 0,
                "submissions": {"ontime": 15, "late": 0}
            }
            for i in range(5)
        ]
    }
    
    response = requests.post(
        f"{BASE_URL}/api/ai/check-alerts/",
        json=cohort_data
    )
    
    if response.status_code == 200:
        result = response.json()
        
        print("\n" + "=" * 60)
        print("TODAY'S ALERTS")
        print("=" * 60)
        print(f"Total Alerts: {result['total_alerts']}")
        print(f"Critical: {result['critical_count']}")
        
        # Cohort-level alerts
        if result['cohort_level']:
            print("\n⚠️  COHORT-LEVEL ALERTS:")
            for alert in result['cohort_level']:
                print(f"  - {alert['message']}")
        
        # Individual critical alerts
        critical = [a for a in result['individual'] if a['severity'] == 'critical']
        if critical:
            print(f"\n🚨 CRITICAL INDIVIDUAL ALERTS ({len(critical)}):")
            for alert in critical:
                print(f"  - {alert['student_id']}: {alert['message']}")
                print(f"    Action: {alert['recommended_action']}")
    
    return response.json()


# ============================================================================
# EXAMPLE 5: Dashboard Insights
# ============================================================================

def example_5_dashboard_insights():
    """Get comprehensive dashboard insights"""
    
    cohort_data = {
        "cohort_id": "Section A - Week 10",
        "students": [
            {
                "student_id": f"S{i:03d}",
                "pace_history": [45 + i*4, 50 + i*4, 55 + i*4, 60 + i*4, 58 + i*4, 60 + i*4],
                "attendance_history": [85 + i, 87 + i, 85 + i, 88 + i, 86 + i, 89 + i],
                "test_scores": {
                    "math": [65 + i*2, 68 + i*2, 70 + i*2, 72 + i*2],
                    "english": [70 + i, 72 + i, 74 + i, 76 + i]
                },
                "absences_current": 0,
                "late_arrivals_current": 0,
                "submissions": {"ontime": 18, "late": 1}
            }
            for i in range(15)  # 15 students
        ]
    }
    
    response = requests.post(
        f"{BASE_URL}/api/ai/insights/",
        json=cohort_data
    )
    
    if response.status_code == 200:
        result = response.json()
        
        print("\n" + "=" * 60)
        print("DASHBOARD INSIGHTS")
        print("=" * 60)
        
        # Display insight cards
        for insight in result['insights']:
            print(f"\n{insight['icon']} {insight['title']}")
            print(f"   {insight['description']}")
            print(f"   → {insight['action']}")
            print(f"   Priority: {insight['priority'].upper()}")
        
        # Risk summary
        summary = result['cohort_summary']
        print(f"\n" + "-" * 60)
        print("RISK SUMMARY")
        print("-" * 60)
        print(f"Students: {summary['total_students']}")
        print(f"At Risk: {summary['high_risk_count']}")
        print(f"Average Risk: {summary['average_risk']}%")
        
        # Forecast
        forecast = result['forecast']
        print(f"\n" + "-" * 60)
        print("END-OF-QUARTER FORECAST")
        print("-" * 60)
        print(f"Predicted Pass Rate: {forecast['predicted_pass_rate']:.0f}%")
        print(f"Predicted Failures: {forecast['predicted_at_risk']}")
        print(f"Confidence: {forecast['confidence']*100:.0f}%")
    
    return response.json()


# ============================================================================
# EXAMPLE 6: Generate Weekly Report
# ============================================================================

def example_6_generate_report():
    """Generate text report for email/PDF"""
    
    current_week = {
        "cohort_id": "Section A - Week 10",
        "students": [
            {
                "student_id": f"S{i:03d}",
                "pace_history": [45 + i*3, 50 + i*3, 55 + i*3, 60 + i*3],
                "attendance_history": [85, 87, 88, 89],
                "test_scores": {"math": [65 + i*2, 68 + i*2]},
                "absences_current": 0,
                "late_arrivals_current": 0,
                "submissions": {"ontime": 15, "late": 1}
            }
            for i in range(10)
        ]
    }
    
    previous_week = {
        "cohort_id": "Section A - Week 9",
        "students": [
            {
                "student_id": f"S{i:03d}",
                "pace_history": [45 + i*3 - 5, 50 + i*3 - 5, 55 + i*3 - 5],
                "attendance_history": [80, 82, 85],
                "test_scores": {"math": [60 + i*2, 65 + i*2]},
                "absences_current": 1,
                "late_arrivals_current": 0,
                "submissions": {"ontime": 10, "late": 3}
            }
            for i in range(10)
        ]
    }
    
    response = requests.post(
        f"{BASE_URL}/api/ai/report/text",
        json={
            "cohort_id": "Section A",
            "students": current_week['students'],
            "previous_data": previous_week
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        print("\n" + result['report'])
    
    return response.json()


# ============================================================================
# EXAMPLE 7: Peer Study Group Recommendations
# ============================================================================

def example_7_peer_groups():
    """Get peer study group recommendations"""
    
    cohort_data = {
        "cohort_id": "Section A",
        "students": [
            {
                "student_id": f"S{i:03d}",
                "pace_history": [50 + i*5, 55 + i*5, 60 + i*5],
                "attendance_history": [85 + i, 87 + i, 89 + i],
                "test_scores": {"math": [65 + i*3, 70 + i*3]},
                "absences_current": 0,
                "late_arrivals_current": 0,
                "submissions": {"ontime": 15 + i, "late": 0}
            }
            for i in range(10)
        ]
    }
    
    response = requests.post(
        f"{BASE_URL}/api/ai/grouping-recommendation/",
        json=cohort_data
    )
    
    if response.status_code == 200:
        result = response.json()
        
        print("\n" + "=" * 60)
        print("PEER STUDY GROUP RECOMMENDATIONS")
        print("=" * 60)
        
        print(f"\nTotal Groups: {result['total_groups']}")
        print(f"Peer Tutors Available: {', '.join(result['peer_tutors'])}")
        
        print("\nGROUPS:")
        for group in result['groupings']:
            print(f"\n  {group['group_name']}")
            if group.get('mentor'):
                print(f"    Mentor: {group['mentor']}")
                print(f"    Mentees: {', '.join(group['mentees'])}")
            else:
                print(f"    Members: {', '.join(group['members'])}")
            print(f"    Focus: {group['focus']}")
            print(f"    Frequency: {group['frequency']}")
    
    return response.json()


# ============================================================================
# EXAMPLE 8: Anomaly Detection
# ============================================================================

def example_8_anomalies():
    """Detect unusual performance patterns"""
    
    cohort_data = {
        "cohort_id": "Section A",
        "students": [
            # Normal student
            {"student_id": "S001", "pace_history": [60, 65, 70], "attendance_history": [90, 91, 92],
             "test_scores": {"math": [75, 78, 80]}, "absences_current": 0, "late_arrivals_current": 0,
             "submissions": {"ontime": 18, "late": 0}},
            
            # Sudden drop
            {"student_id": "S002", "pace_history": [80, 70, 50], "attendance_history": [95, 90, 60],
             "test_scores": {"math": [85, 80, 40]}, "absences_current": 5, "late_arrivals_current": 3,
             "submissions": {"ontime": 18, "late": 5}},
            
            # Unexpected success
            {"student_id": "S003", "pace_history": [45, 50, 55], "attendance_history": [70, 75, 80],
             "test_scores": {"math": [60, 65, 75]}, "absences_current": 1, "late_arrivals_current": 0,
             "submissions": {"ontime": 15, "late": 1}},
        ]
    }
    
    response = requests.post(
        f"{BASE_URL}/api/ai/anomalies/",
        json=cohort_data
    )
    
    if response.status_code == 200:
        result = response.json()
        
        print("\n" + "=" * 60)
        print("ANOMALIES DETECTED")
        print("=" * 60)
        
        for anomaly in result:
            print(f"\n{anomaly['student_id']}")
            print(f"  Type: {anomaly['type'].replace('_', ' ').upper()}")
            print(f"  Description: {anomaly['description']}")
            print(f"  Severity: {anomaly['severity'].upper()}")
            print(f"  Recommendation: {anomaly['recommendation']}")
    
    return response.json()


# ============================================================================
# EXAMPLE 9: System Health & Info
# ============================================================================

def example_9_system_info():
    """Check system health and get info"""
    
    # Health check
    health_response = requests.get(f"{BASE_URL}/api/ai/health")
    
    # System info
    info_response = requests.get(f"{BASE_URL}/api/ai/info")
    
    if health_response.status_code == 200 and info_response.status_code == 200:
        health = health_response.json()
        info = info_response.json()
        
        print("\n" + "=" * 60)
        print("SYSTEM STATUS")
        print("=" * 60)
        print(f"Status: {health['status'].upper()}")
        print(f"Timestamp: {health['timestamp']}")
        
        print("\nMODULES:")
        for module, status in health['modules'].items():
            print(f"  ✅ {module}: {status}")
        
        print(f"\n\nSYSTEM INFO")
        print("=" * 60)
        print(f"System: {info['system']}")
        print(f"Version: {info['version']}")
        print(f"Features: {len(info['features'])} available")
        
        print("\nFEATURES:")
        for feature in info['features']:
            print(f"  • {feature}")


# ============================================================================
# MAIN: Run all examples
# ============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("LBCA AI MONITORING SYSTEM - COMPLETE EXAMPLES")
    print("=" * 60)
    
    try:
        # Test each example
        print("\n\n[1/9] Running: Single Student Risk Check")
        example_1_single_student_risk()
        
        print("\n\n[2/9] Running: Cohort Risk Analysis")
        example_2_cohort_analysis()
        
        print("\n\n[3/9] Running: Get Recommendations")
        example_3_recommendations()
        
        print("\n\n[4/9] Running: Daily Alert Check")
        example_4_daily_alert_check()
        
        print("\n\n[5/9] Running: Dashboard Insights")
        example_5_dashboard_insights()
        
        print("\n\n[6/9] Running: Generate Report")
        example_6_generate_report()
        
        print("\n\n[7/9] Running: Peer Group Recommendations")
        example_7_peer_groups()
        
        print("\n\n[8/9] Running: Anomaly Detection")
        example_8_anomalies()
        
        print("\n\n[9/9] Running: System Info")
        example_9_system_info()
        
        print("\n\n" + "=" * 60)
        print("ALL EXAMPLES COMPLETED SUCCESSFULLY! ✅")
        print("=" * 60)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to API server")
        print("Make sure the server is running:")
        print("  python -m uvicorn app.main:app --reload")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
