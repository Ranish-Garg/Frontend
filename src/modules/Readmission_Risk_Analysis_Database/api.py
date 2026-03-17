"""
API layer for Readmission Risk Analysis (Module 34)
Covers: CRUD, analytical queries, aggregations, trigger-like logic
"""

from datetime import datetime
from .db import get_db


# ─────────────────────────────────────────────
# PATIENTS
# ─────────────────────────────────────────────

def add_patient(data: dict):
    db = get_db()
    db.patients.insert_one(data)
    return {"status": "ok", "patient_id": data["patient_id"]}

def get_patient(patient_id: str):
    db = get_db()
    return db.patients.find_one({"patient_id": patient_id}, {"_id": 0})

def get_all_patients():
    db = get_db()
    return list(db.patients.find({}, {"_id": 0}))

def update_patient(patient_id: str, updates: dict):
    db = get_db()
    db.patients.update_one({"patient_id": patient_id}, {"$set": updates})
    return {"status": "updated"}

def delete_patient(patient_id: str):
    db = get_db()
    db.patients.delete_one({"patient_id": patient_id})
    return {"status": "deleted"}


# ─────────────────────────────────────────────
# READMISSIONS
# ─────────────────────────────────────────────

def add_readmission(data: dict):
    """Insert readmission and auto-trigger risk score calculation."""
    db = get_db()
    db.readmissions.insert_one(data)
    # Trigger: auto-calculate risk score on new readmission
    _trigger_risk_score(data)
    return {"status": "ok", "rr_id": data["rr_id"]}

def get_readmission(rr_id: str):
    db = get_db()
    return db.readmissions.find_one({"rr_id": rr_id}, {"_id": 0})

def get_patient_readmissions(patient_id: str):
    db = get_db()
    return list(db.readmissions.find({"patient_id": patient_id}, {"_id": 0}))

def get_all_readmissions():
    db = get_db()
    return list(db.readmissions.find({}, {"_id": 0}))

def update_readmission(rr_id: str, updates: dict):
    db = get_db()
    db.readmissions.update_one({"rr_id": rr_id}, {"$set": updates})
    return {"status": "updated"}

def delete_readmission(rr_id: str):
    db = get_db()
    db.readmissions.delete_one({"rr_id": rr_id})
    return {"status": "deleted"}

def get_preventable_readmissions():
    db = get_db()
    return list(db.readmissions.find({"preventable_flag": True}, {"_id": 0}))

def get_readmissions_by_chronic_type(type_chronic: str):
    db = get_db()
    return list(db.readmissions.find({"type_chronic": type_chronic}, {"_id": 0}))


# ─────────────────────────────────────────────
# RISK SCORES
# ─────────────────────────────────────────────

def add_risk_score(data: dict):
    db = get_db()
    db.risk_scores.insert_one(data)
    return {"status": "ok", "rs_id": data["rs_id"]}

def get_risk_score(rs_id: str):
    db = get_db()
    return db.risk_scores.find_one({"rs_id": rs_id}, {"_id": 0})

def get_scores_by_patient(patient_id: str):
    db = get_db()
    return list(db.risk_scores.find({"patient_id": patient_id}, {"_id": 0}))

def get_high_risk_patients():
    """Returns patients with High risk category with their details."""
    db = get_db()
    scores = list(db.risk_scores.find({"risk_category": "High"}, {"_id": 0}))
    result = []
    for s in scores:
        patient = db.patients.find_one({"patient_id": s["patient_id"]}, {"_id": 0})
        result.append({"patient": patient, "risk_score": s})
    return result

def get_risk_category_distribution():
    """Aggregation: count of patients per risk category."""
    db = get_db()
    pipeline = [
        {"$group": {"_id": "$risk_category", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    return list(db.risk_scores.aggregate(pipeline))

def get_average_score_by_model():
    """Aggregation: average risk score per model."""
    db = get_db()
    pipeline = [
        {"$group": {"_id": "$model_id", "avg_score": {"$avg": "$score_value"}, "count": {"$sum": 1}}},
        {"$sort": {"avg_score": -1}}
    ]
    return list(db.risk_scores.aggregate(pipeline))


# ─────────────────────────────────────────────
# RISK FACTORS
# ─────────────────────────────────────────────

def add_risk_factor(data: dict):
    db = get_db()
    db.risk_factors.insert_one(data)
    return {"status": "ok", "rf_id": data["rf_id"]}

def get_factors_by_score(rs_id: str):
    db = get_db()
    return list(db.risk_factors.find({"rs_id": rs_id}, {"_id": 0}))

def get_factors_by_type(factor_type: str):
    db = get_db()
    return list(db.risk_factors.find({"factor_type": factor_type}, {"_id": 0}))

def get_most_common_risk_factors():
    """Aggregation: most frequently occurring risk factor types."""
    db = get_db()
    pipeline = [
        {"$group": {"_id": "$factor_type", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    return list(db.risk_factors.aggregate(pipeline))


# ─────────────────────────────────────────────
# INTERVENTIONS
# ─────────────────────────────────────────────

def add_intervention(data: dict):
    db = get_db()
    db.interventions.insert_one(data)
    return {"status": "ok", "intervention_id": data["intervention_id"]}

def get_interventions_by_readmission(rr_id: str):
    db = get_db()
    return list(db.interventions.find({"rr_ids": rr_id}, {"_id": 0}))

def get_interventions_by_status(status: str):
    db = get_db()
    return list(db.interventions.find({"status": status}, {"_id": 0}))

def update_intervention_status(intervention_id: str, status: str):
    db = get_db()
    db.interventions.update_one(
        {"intervention_id": intervention_id},
        {"$set": {"status": status}}
    )
    return {"status": "updated"}


# ─────────────────────────────────────────────
# PREVENTION STRATEGIES
# ─────────────────────────────────────────────

def add_prevention_strategy(data: dict):
    db = get_db()
    db.prevention_strategies.insert_one(data)
    return {"status": "ok", "strategy_id": data["strategy_id"]}

def get_strategies_by_readmission(rr_id: str):
    db = get_db()
    return list(db.prevention_strategies.find({"rr_ids": rr_id}, {"_id": 0}))

def get_all_strategies():
    db = get_db()
    return list(db.prevention_strategies.find({}, {"_id": 0}))


# ─────────────────────────────────────────────
# QUALITY METRICS
# ─────────────────────────────────────────────

def add_quality_metric(data: dict):
    db = get_db()
    db.quality_metrics.insert_one(data)
    return {"status": "ok", "report_id": data["report_id"]}

def get_metrics_by_strategy(strategy_id: str):
    db = get_db()
    return list(db.quality_metrics.find({"strategy_id": strategy_id}, {"_id": 0}))

def get_metrics_by_period(reporting_period: str):
    db = get_db()
    return list(db.quality_metrics.find({"reporting_period": reporting_period}, {"_id": 0}))

def get_metric_trend(metric_name: str):
    """Aggregation: average value of a metric across all periods."""
    db = get_db()
    pipeline = [
        {"$match": {"metric_name": metric_name}},
        {"$group": {"_id": "$reporting_period", "avg_value": {"$avg": "$value"}}},
        {"$sort": {"_id": 1}}
    ]
    return list(db.quality_metrics.aggregate(pipeline))


# ─────────────────────────────────────────────
# COMPLEX / JOINED QUERIES
# ─────────────────────────────────────────────

def get_full_readmission_report(rr_id: str):
    """Full report: readmission + patient + risk score + factors + interventions + strategies."""
    db = get_db()
    readmission = db.readmissions.find_one({"rr_id": rr_id}, {"_id": 0})
    if not readmission:
        return None
    patient  = db.patients.find_one({"patient_id": readmission["patient_id"]}, {"_id": 0})
    score    = db.risk_scores.find_one({"rr_id": rr_id}, {"_id": 0})
    factors  = list(db.risk_factors.find({"rs_id": score["rs_id"]}, {"_id": 0})) if score else []
    interventions = list(db.interventions.find({"rr_ids": rr_id}, {"_id": 0}))
    strategies    = list(db.prevention_strategies.find({"rr_ids": rr_id}, {"_id": 0}))
    return {
        "patient": patient,
        "readmission": readmission,
        "risk_score": score,
        "risk_factors": factors,
        "interventions": interventions,
        "prevention_strategies": strategies
    }

def get_readmission_summary_stats():
    """Dashboard stats: total readmissions, preventable count, avg length of stay, risk breakdown."""
    db = get_db()
    total        = db.readmissions.count_documents({})
    preventable  = db.readmissions.count_documents({"preventable_flag": True})
    ar_flagged   = db.readmissions.count_documents({"ar_flag": True})
    avg_los      = list(db.readmissions.aggregate([
        {"$group": {"_id": None, "avg_los": {"$avg": "$length_of_stay"}}}
    ]))
    risk_dist    = get_risk_category_distribution()
    return {
        "total_readmissions": total,
        "preventable": preventable,
        "ar_flagged": ar_flagged,
        "avg_length_of_stay": round(avg_los[0]["avg_los"], 2) if avg_los else 0,
        "risk_distribution": risk_dist
    }


# ─────────────────────────────────────────────
# TRIGGER-LIKE LOGIC
# ─────────────────────────────────────────────

def _trigger_risk_score(readmission: dict):
    """
    Auto-generate a basic risk score when a new readmission is added.
    Uses simple rule: LOS > 7 → High, 4-7 → Medium, <4 → Low
    """
    db = get_db()
    los = readmission.get("length_of_stay", 0)
    if los > 7:
        category, score = "High", 8.0
    elif los >= 4:
        category, score = "Medium", 5.0
    else:
        category, score = "Low", 2.5

    rs_id = f"RS_AUTO_{readmission['rr_id']}"
    existing = db.risk_scores.find_one({"rs_id": rs_id})
    if not existing:
        db.risk_scores.insert_one({
            "rs_id": rs_id,
            "patient_id": readmission["patient_id"],
            "rr_id": readmission["rr_id"],
            "model_id": "RM001",
            "score_value": score,
            "risk_category": category,
            "risk_calculation_date": datetime.today().strftime("%Y-%m-%d")
        })

# Change by PrathamandX on Tue Mar 17 14:22:00 2026 +0530
