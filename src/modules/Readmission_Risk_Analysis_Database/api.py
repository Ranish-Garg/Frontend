"""
API layer for Readmission Risk Analysis (Module 34)
Full pipeline: input → model selection → score → DB → trigger → intervention + strategy
"""

from datetime import datetime, date
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
# RISK MODELS
# ─────────────────────────────────────────────

def get_all_models():
    db = get_db()
    return list(db.risk_models.find({}, {"_id": 0}))

def get_model(model_id: str):
    db = get_db()
    return db.risk_models.find_one({"model_id": model_id}, {"_id": 0})


# ─────────────────────────────────────────────
# READMISSIONS
# ─────────────────────────────────────────────

def add_readmission(data: dict):
    db = get_db()
    db.readmissions.insert_one(data)
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
    db = get_db()
    scores = list(db.risk_scores.find({"risk_category": "High"}, {"_id": 0}))
    result = []
    for s in scores:
        patient = db.patients.find_one({"patient_id": s["patient_id"]}, {"_id": 0})
        result.append({"patient": patient, "risk_score": s})
    return result

def get_risk_category_distribution():
    db = get_db()
    pipeline = [
        {"$group": {"_id": "$risk_category", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    return list(db.risk_scores.aggregate(pipeline))

def get_average_score_by_model():
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

def get_most_common_risk_factors():
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


# ─────────────────────────────────────────────
# COMPLEX QUERIES
# ─────────────────────────────────────────────

def get_full_readmission_report(rr_id: str):
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
    db = get_db()
    total       = db.readmissions.count_documents({})
    preventable = db.readmissions.count_documents({"preventable_flag": True})
    ar_flagged  = db.readmissions.count_documents({"ar_flag": True})
    avg_los     = list(db.readmissions.aggregate([
        {"$group": {"_id": None, "avg_los": {"$avg": "$length_of_stay"}}}
    ]))
    risk_dist   = get_risk_category_distribution()
    return {
        "total_readmissions": total,
        "preventable": preventable,
        "ar_flagged": ar_flagged,
        "avg_length_of_stay": round(avg_los[0]["avg_los"], 2) if avg_los else 0,
        "risk_distribution": risk_dist
    }


# ─────────────────────────────────────────────
# FULL PIPELINE
# ─────────────────────────────────────────────

# Thresholds
HIGH_RISK_THRESHOLD = 7.0
MEDIUM_RISK_THRESHOLD = 4.0

# Model selection rules based on input
def select_model(los: int, has_oncology: bool, has_lab_abnormality: bool) -> str:
    """
    Select scoring model based on clinical inputs:
    - HOSPITAL model: oncology or lab abnormality present
    - BOOST model: short stay (LOS < 4) with no comorbidities
    - LACE model: default
    """
    if has_oncology or has_lab_abnormality:
        return "RM002"  # HOSPITAL Score
    elif los < 4:
        return "RM003"  # BOOST Score
    else:
        return "RM001"  # LACE Score (default)


def calculate_score(model_id: str, los: int, num_comorbidities: int,
                    prior_ed_visits: int, is_acute: bool) -> float:
    """
    Calculate risk score based on selected model and clinical inputs.
    LACE:     L(LOS) + A(acuity) + C(comorbidities) + E(ED visits)
    HOSPITAL: simplified weighted score
    BOOST:    simplified weighted score
    """
    if model_id == "RM001":  # LACE
        l = min(los, 7)                          # max 7 pts
        a = 3 if is_acute else 0                 # acuity
        c = min(num_comorbidities * 2, 5)        # max 5 pts
        e = min(prior_ed_visits * 1.5, 4)        # max 4 pts
        return round(l + a + c + e, 2)

    elif model_id == "RM002":  # HOSPITAL
        h = min(los * 0.5, 3)
        o = num_comorbidities * 1.5
        e = prior_ed_visits * 1.0
        return round(h + o + e, 2)

    else:  # BOOST (RM003)
        return round((los * 0.3) + (num_comorbidities * 1.0) + (prior_ed_visits * 0.5), 2)


def score_to_category(score: float) -> str:
    if score >= HIGH_RISK_THRESHOLD:
        return "High"
    elif score >= MEDIUM_RISK_THRESHOLD:
        return "Medium"
    return "Low"


def _get_next_id(collection, prefix: str, id_field: str) -> str:
    last = collection.find_one(
        {id_field: {"$regex": f"^{prefix}"}},
        sort=[(id_field, -1)]
    )
    if last:
        num = int(last[id_field].replace(prefix, "")) + 1
    else:
        num = 1
    return f"{prefix}{num:03d}"


def run_pipeline(
    patient_id: str,
    admission_date: str,
    discharge_date: str,
    los: int,
    type_chronic: str,
    is_acute: bool,
    ar_flag: bool,
    num_comorbidities: int,
    prior_ed_visits: int,
    has_oncology: bool,
    has_lab_abnormality: bool,
    selected_factors: list
) -> dict:
    """
    Full pipeline:
    1. Save readmission record
    2. Select model based on inputs
    3. Calculate risk score
    4. Save risk score + risk factors to DB
    5. If score >= threshold → trigger intervention + assign prevention strategy
    6. Return full result
    """
    db = get_db()
    today = datetime.today().strftime("%Y-%m-%d")

    # Check preventable (readmission within 30 days)
    preventable = False
    prior = db.readmissions.find_one(
        {"patient_id": patient_id},
        sort=[("discharge_date", -1)]
    )
    if prior and prior.get("discharge_date"):
        try:
            prev_discharge = datetime.strptime(prior["discharge_date"], "%Y-%m-%d")
            adm = datetime.strptime(admission_date, "%Y-%m-%d")
            preventable = (adm - prev_discharge).days <= 30
        except Exception:
            pass

    # 1. Save readmission
    rr_id = _get_next_id(db.readmissions, "RR", "rr_id")
    readmission = {
        "rr_id": rr_id,
        "patient_id": patient_id,
        "prior_id": prior["rr_id"] if prior else None,
        "admission_date": admission_date,
        "discharge_date": discharge_date,
        "length_of_stay": los,
        "readmission_date": None,
        "status_to_chronic": "Acute" if is_acute else "Chronic",
        "type_chronic": type_chronic,
        "ar_flag": ar_flag,
        "preventable_flag": preventable
    }
    db.readmissions.insert_one(readmission)

    # 2. Select model
    model_id = select_model(los, has_oncology, has_lab_abnormality)

    # 3. Calculate score
    score_value = calculate_score(model_id, los, num_comorbidities, prior_ed_visits, is_acute)
    category    = score_to_category(score_value)

    # 4. Save risk score
    rs_id = _get_next_id(db.risk_scores, "RS", "rs_id")
    risk_score = {
        "rs_id": rs_id,
        "patient_id": patient_id,
        "rr_id": rr_id,
        "model_id": model_id,
        "score_value": score_value,
        "risk_category": category,
        "risk_calculation_date": today
    }
    db.risk_scores.insert_one(risk_score)

    # Save risk factors
    rf_ids = []
    for i, factor in enumerate(selected_factors):
        rf_id = _get_next_id(db.risk_factors, "RF", "rf_id")
        db.risk_factors.insert_one({
            "rf_id": rf_id,
            "factor_name": factor["name"],
            "factor_type": factor["type"],
            "description": factor.get("description", ""),
            "rs_id": rs_id
        })
        rf_ids.append(rf_id)

    # 5. Trigger intervention + prevention strategy if High or Medium risk
    triggered_intervention = None
    assigned_strategy = None

    if category in ("High", "Medium"):
        # Trigger intervention
        in_id = _get_next_id(db.interventions, "IN", "intervention_id")
        int_name = "Urgent Care Coordination" if category == "High" else "Follow-up Appointment"
        int_type = "Clinical" if category == "High" else "Outpatient"
        triggered_intervention = {
            "intervention_id": in_id,
            "intervention_name": int_name,
            "type": int_type,
            "start_date": today,
            "end_date": None,
            "status": "Ongoing",
            "rr_ids": [rr_id],
            "rf_ids": rf_ids
        }
        db.interventions.insert_one(triggered_intervention)

        # Assign prevention strategy — fallback to any available strategy
        strategy = db.prevention_strategies.find_one(
            {"category": "Post-Discharge" if category == "High" else "Outpatient"},
            {"_id": 0}
        )
        if not strategy:
            strategy = db.prevention_strategies.find_one({}, {"_id": 0})
        if strategy:
            db.prevention_strategies.update_one(
                {"strategy_id": strategy["strategy_id"]},
                {"$addToSet": {"rr_ids": rr_id}}
            )
            assigned_strategy = strategy

    return {
        "rr_id": rr_id,
        "model_used": model_id,
        "score_value": score_value,
        "risk_category": category,
        "preventable": preventable,
        "triggered_intervention": triggered_intervention,
        "assigned_strategy": assigned_strategy
    }
