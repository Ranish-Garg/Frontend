"""
Common queries for Readmission Risk Analysis (Module 34)
"""

from .db import get_db


def get_patient_readmissions(patient_id: str):
    """All readmissions for a patient with their risk scores."""
    db = get_db()
    readmissions = list(db.readmissions.find({"patient_id": patient_id}, {"_id": 0}))
    for r in readmissions:
        r["risk_scores"] = list(db.risk_scores.find({"rr_id": r["rr_id"]}, {"_id": 0}))
    return readmissions


def get_high_risk_patients():
    """Patients with High risk category scores."""
    db = get_db()
    scores = list(db.risk_scores.find({"risk_category": "High"}, {"_id": 0}))
    result = []
    for s in scores:
        patient = db.patients.find_one({"patient_id": s["patient_id"]}, {"_id": 0})
        result.append({"patient": patient, "risk_score": s})
    return result


def get_readmission_with_factors(rr_id: str):
    """Full readmission record with associated risk factors and interventions."""
    db = get_db()
    readmission = db.readmissions.find_one({"rr_id": rr_id}, {"_id": 0})
    if not readmission:
        return None
    score = db.risk_scores.find_one({"rr_id": rr_id}, {"_id": 0})
    factors = list(db.risk_factors.find({"rs_id": score["rs_id"]}, {"_id": 0})) if score else []
    interventions = list(db.interventions.find({"rr_ids": rr_id}, {"_id": 0}))
    strategies = list(db.prevention_strategies.find({"rr_ids": rr_id}, {"_id": 0}))
    return {
        "readmission": readmission,
        "risk_score": score,
        "risk_factors": factors,
        "interventions": interventions,
        "prevention_strategies": strategies
    }


def get_quality_metrics_by_strategy(strategy_id: str):
    """Quality metrics for a given prevention strategy."""
    db = get_db()
    return list(db.quality_metrics.find({"strategy_id": strategy_id}, {"_id": 0}))


def get_preventable_readmissions():
    """All readmissions flagged as preventable."""
    db = get_db()
    return list(db.readmissions.find({"preventable_flag": True}, {"_id": 0}))


def get_readmission_rate_summary():
    """Count of readmissions grouped by risk category."""
    db = get_db()
    pipeline = [
        {"$group": {"_id": "$risk_category", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    return list(db.risk_scores.aggregate(pipeline))

# Change by pokasireesha2303 on Mon Mar 16 18:22:00 2026 +0530
