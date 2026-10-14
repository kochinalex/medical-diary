from datetime import datetime, date
from typing import List, Dict, Any

def calculate_days_ago(date_str: str) -> int:
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d").date()
        today = date.today()
        return (today - dt).days
    except Exception:
        return 0

def generate_health_advisory(records: List[Dict[str, Any]],
                             biomarkers: Dict[str, List[Dict[str, Any]]],
                             reminders: List[Dict[str, Any]],
                             profile: Dict[str, Any]) -> Dict[str, Any]:
    insights = []
    actions = []
    upcoming_alerts = []

    # 1. Analyze Biomarker Trends
    for name, history in biomarkers.items():
        if not history:
            continue
        latest = history[-1]
        val = latest["value"]
        unit = latest["unit"]
        flag = latest.get("flag", "NORMAL")
        test_date = latest["test_date"]

        if name.lower() == "ferritin":
            if flag == "LOW":
                trend_msg = ""
                if len(history) > 1:
                    prev = history[-2]["value"]
                    diff = val - prev
                    if diff > 0:
                        trend_msg = f" (Trending upward from {prev} {unit}, +{diff:.1f} {unit})"
                insights.append({
                    "type": "warning",
                    "category": "Lab Finding",
                    "title": f"Low Iron Stores (Ferritin: {val} {unit}{trend_msg})",
                    "message": f"Ferritin remains below reference range ({latest['ref_min']}-{latest['ref_max']} {unit}).",
                    "advice": "Take oral iron with Vitamin C to double absorption. Avoid tea, coffee, and calcium within 2 hours of taking iron. Retest in 8-12 weeks."
                })
                actions.append({
                    "action": "Schedule repeat Ferritin & Complete Blood Count (CBC) test in 60-90 days",
                    "priority": "Medium",
                    "link": "reminders"
                })

        elif name.lower() == "vitamin d":
            if flag == "LOW":
                insights.append({
                    "type": "info",
                    "category": "Lab Finding",
                    "title": f"Suboptimal Vitamin D ({val} {unit})",
                    "message": f"Optimal level is >30 {unit}. Entering autumn/winter seasons will naturally reduce synthesis.",
                    "advice": "Continue maintenance supplementation (2000-4000 IU daily with dietary fats). Check serum 25(OH)D at next annual exam."
                })

        elif name.lower() in ["total cholesterol", "ldl"]:
            if flag == "HIGH":
                insights.append({
                    "type": "warning",
                    "category": "Cardiovascular",
                    "title": f"Elevated {name} ({val} {unit})",
                    "message": f"Above recommended baseline ({latest['ref_max']} {unit}).",
                    "advice": "Incorporate soluble fibers (oats, psyllium), omega-3s, and 150 min/week moderate aerobic exercise. Review family cardiovascular history with GP."
                })

    # 2. Analyze Due Screenings and Calendar
    today = date.today()
    for rem in reminders:
        if rem.get("completed", 0) == 1:
            continue
        try:
            due_dt = datetime.strptime(rem["due_date"], "%Y-%m-%d").date()
            diff_days = (due_dt - today).days
            if diff_days < 0:
                upcoming_alerts.append({
                    "status": "overdue",
                    "title": rem["title"],
                    "due_date": rem["due_date"],
                    "notes": rem.get("notes", ""),
                    "days_label": f"Overdue by {abs(diff_days)} days"
                })
            elif diff_days <= 45:
                upcoming_alerts.append({
                    "status": "upcoming",
                    "title": rem["title"],
                    "due_date": rem["due_date"],
                    "notes": rem.get("notes", ""),
                    "days_label": f"Due in {diff_days} days"
                })
        except Exception:
            pass

    # 3. Preventive Health Schedule Gaps
    # Check last dental visit
    last_dental = next((r for r in records if "dental" in r["title"].lower() or "teeth" in r["title"].lower()), None)
    if not last_dental:
        actions.append({
            "action": "Book Bi-annual Dental Checkup & Hygiene Cleaning",
            "priority": "High",
            "link": "calendar"
        })

    # Check last skin check
    mole_rem = next((r for r in reminders if "mole" in r["title"].lower() or "derma" in r["title"].lower()), None)
    if mole_rem and not mole_rem.get("completed", 0):
        insights.append({
            "type": "info",
            "category": "Preventive Screening",
            "title": "Annual Full-Body Skin Examination Due Soon",
            "message": "Following up on your Nov 2025 dysplastic mole removal. Annual surveillance is recommended.",
            "advice": "Monitor skin using the ABCDE criteria (Asymmetry, Border, Color, Diameter, Evolution). Schedule full-body dermoscopy."
        })

    # 4. Generate Pre-Visit Doctor Brief
    doctor_brief = generate_doctor_brief(records, biomarkers, profile)

    return {
        "insights": insights,
        "actions": actions,
        "alerts": upcoming_alerts,
        "doctor_brief": doctor_brief
    }

def generate_doctor_brief(records: List[Dict[str, Any]],
                          biomarkers: Dict[str, List[Dict[str, Any]]],
                          profile: Dict[str, Any]) -> str:
    lines = []
    lines.append(f"PATIENT BRIEF: {profile.get('name', 'Patient')}")
    lines.append(f"DOB: {profile.get('birth_date', 'N/A')} | Blood Group: {profile.get('blood_type', 'N/A')}")
    lines.append(f"Known Allergies: {profile.get('allergies', 'None reported')}")
    lines.append(f"Active Conditions: {profile.get('chronic_conditions', 'None')}")
    lines.append(f"Current Regimen / Meds: {profile.get('current_medications', 'None')}")
    lines.append("-" * 40)
    lines.append("KEY RECENT LABS:")
    for b_name in ["Ferritin", "Vitamin D", "Fasting Glucose", "Total Cholesterol"]:
        if b_name in biomarkers and biomarkers[b_name]:
            latest = biomarkers[b_name][-1]
            lines.append(f"  * {b_name}: {latest['value']} {latest['unit']} ({latest['flag']}) on {latest['test_date']}")
    lines.append("-" * 40)
    lines.append("RECENT CLINICAL EVENTS (Past 12 Months):")
    recent_events = records[:4]
    for ev in recent_events:
        lines.append(f"  * [{ev['event_date']}] {ev['title']} ({ev['provider'] or 'Self'}): {ev['notes'][:80]}...")

    return "\n".join(lines)
