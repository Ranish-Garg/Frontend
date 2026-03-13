"""
Seed script — inserts sample data for all Readmission Risk Analysis collections.
Run: python -m src.modules.Readmission_Risk_Analysis_Database.seed
"""

from .db import get_db, setup_collections

def seed():
    setup_collections()
    db = get_db()

    patients = [
        {"patient_id": "P001", "first_name": "Arjun",  "last_name": "Sharma",   "dob": "1965-03-12", "age": 59, "gender": "Male",   "email": "arjun@email.com",  "contact": "9876543210", "insurance_id": "INS001", "mobile_no": "9876543210"},
        {"patient_id": "P002", "first_name": "Priya",  "last_name": "Mehta",    "dob": "1978-07-22", "age": 46, "gender": "Female", "email": "priya@email.com",  "contact": "9123456780", "insurance_id": "INS002", "mobile_no": "9123456780"},
        {"patient_id": "P003", "first_name": "Ramesh", "last_name": "Patil",    "dob": "1952-11-05", "age": 72, "gender": "Male",   "email": "ramesh@email.com", "contact": "9988776655", "insurance_id": "INS003", "mobile_no": "9988776655"},
        {"patient_id": "P004", "first_name": "Sunita", "last_name": "Desai",    "dob": "1970-06-18", "age": 54, "gender": "Female", "email": "sunita@email.com", "contact": "9871234560", "insurance_id": "INS004", "mobile_no": "9871234560"},
        {"patient_id": "P005", "first_name": "Vikram", "last_name": "Nair",     "dob": "1948-09-30", "age": 76, "gender": "Male",   "email": "vikram@email.com", "contact": "9765432100", "insurance_id": "INS005", "mobile_no": "9765432100"},
        {"patient_id": "P006", "first_name": "Anjali", "last_name": "Kulkarni", "dob": "1983-12-01", "age": 41, "gender": "Female", "email": "anjali@email.com", "contact": "9654321098", "insurance_id": "INS006", "mobile_no": "9654321098"},
        {"patient_id": "P007", "first_name": "Deepak", "last_name": "Joshi",    "dob": "1960-04-25", "age": 64, "gender": "Male",   "email": "deepak@email.com", "contact": "9543210987", "insurance_id": "INS007", "mobile_no": "9543210987"},
        {"patient_id": "P008", "first_name": "Meena",  "last_name": "Iyer",     "dob": "1955-08-14", "age": 69, "gender": "Female", "email": "meena@email.com",  "contact": "9432109876", "insurance_id": "INS008", "mobile_no": "9432109876"},
    ]
    _upsert_many(db.patients, patients, "patient_id")

    models = [
        {"model_id": "RM001", "model_name": "LACE Score Model",    "version": "1.0", "description": "Length of stay, Acuity, Comorbidities, ED visits"},
        {"model_id": "RM002", "model_name": "HOSPITAL Score Model","version": "2.1", "description": "Hemoglobin, Oncology, Sodium, Procedure, Insurance, Length, Admission type"},
        {"model_id": "RM003", "model_name": "BOOST Score Model",   "version": "1.5", "description": "Blood urea nitrogen, Oncology, Oxygen, Surgery, Team"},
    ]
    _upsert_many(db.risk_models, models, "model_id")

    readmissions = [
        {"rr_id": "RR001", "patient_id": "P001", "prior_id": None,    "admission_date": "2025-01-10", "discharge_date": "2025-01-17", "length_of_stay": 7,  "readmission_date": "2025-02-01", "status_to_chronic": "Chronic", "type_chronic": "Heart Failure", "ar_flag": True,  "preventable_flag": True},
        {"rr_id": "RR002", "patient_id": "P002", "prior_id": None,    "admission_date": "2025-02-05", "discharge_date": "2025-02-10", "length_of_stay": 5,  "readmission_date": None,          "status_to_chronic": "Acute",   "type_chronic": "Pneumonia",     "ar_flag": False, "preventable_flag": False},
        {"rr_id": "RR003", "patient_id": "P003", "prior_id": "RR001", "admission_date": "2025-03-01", "discharge_date": "2025-03-08", "length_of_stay": 7,  "readmission_date": "2025-03-20", "status_to_chronic": "Chronic", "type_chronic": "COPD",          "ar_flag": True,  "preventable_flag": True},
        {"rr_id": "RR004", "patient_id": "P004", "prior_id": None,    "admission_date": "2025-03-15", "discharge_date": "2025-03-19", "length_of_stay": 4,  "readmission_date": None,          "status_to_chronic": "Acute",   "type_chronic": "Diabetes",      "ar_flag": False, "preventable_flag": False},
        {"rr_id": "RR005", "patient_id": "P005", "prior_id": "RR003", "admission_date": "2025-04-02", "discharge_date": "2025-04-12", "length_of_stay": 10, "readmission_date": "2025-04-25", "status_to_chronic": "Chronic", "type_chronic": "Heart Failure", "ar_flag": True,  "preventable_flag": True},
        {"rr_id": "RR006", "patient_id": "P006", "prior_id": None,    "admission_date": "2025-04-20", "discharge_date": "2025-04-23", "length_of_stay": 3,  "readmission_date": None,          "status_to_chronic": "Acute",   "type_chronic": "Infection",     "ar_flag": False, "preventable_flag": False},
        {"rr_id": "RR007", "patient_id": "P007", "prior_id": "RR002", "admission_date": "2025-05-05", "discharge_date": "2025-05-14", "length_of_stay": 9,  "readmission_date": "2025-05-28", "status_to_chronic": "Chronic", "type_chronic": "COPD",          "ar_flag": True,  "preventable_flag": True},
        {"rr_id": "RR008", "patient_id": "P008", "prior_id": None,    "admission_date": "2025-06-01", "discharge_date": "2025-06-06", "length_of_stay": 5,  "readmission_date": None,          "status_to_chronic": "Acute",   "type_chronic": "Pneumonia",     "ar_flag": False, "preventable_flag": False},
    ]
    _upsert_many(db.readmissions, readmissions, "rr_id")

    scores = [
        {"rs_id": "RS001", "patient_id": "P001", "rr_id": "RR001", "model_id": "RM001", "score_value": 8.5, "risk_category": "High",   "risk_calculation_date": "2025-01-17"},
        {"rs_id": "RS002", "patient_id": "P002", "rr_id": "RR002", "model_id": "RM001", "score_value": 3.2, "risk_category": "Low",    "risk_calculation_date": "2025-02-10"},
        {"rs_id": "RS003", "patient_id": "P003", "rr_id": "RR003", "model_id": "RM002", "score_value": 6.7, "risk_category": "Medium", "risk_calculation_date": "2025-03-08"},
        {"rs_id": "RS004", "patient_id": "P004", "rr_id": "RR004", "model_id": "RM001", "score_value": 4.1, "risk_category": "Medium", "risk_calculation_date": "2025-03-19"},
        {"rs_id": "RS005", "patient_id": "P005", "rr_id": "RR005", "model_id": "RM002", "score_value": 9.2, "risk_category": "High",   "risk_calculation_date": "2025-04-12"},
        {"rs_id": "RS006", "patient_id": "P006", "rr_id": "RR006", "model_id": "RM003", "score_value": 2.1, "risk_category": "Low",    "risk_calculation_date": "2025-04-23"},
        {"rs_id": "RS007", "patient_id": "P007", "rr_id": "RR007", "model_id": "RM002", "score_value": 7.8, "risk_category": "High",   "risk_calculation_date": "2025-05-14"},
        {"rs_id": "RS008", "patient_id": "P008", "rr_id": "RR008", "model_id": "RM003", "score_value": 3.5, "risk_category": "Low",    "risk_calculation_date": "2025-06-06"},
    ]
    _upsert_many(db.risk_scores, scores, "rs_id")

    factors = [
        {"rf_id": "RF001", "factor_name": "Heart Failure",     "factor_type": "Comorbidity", "description": "Chronic heart failure diagnosis",          "rs_id": "RS001"},
        {"rf_id": "RF002", "factor_name": "Polypharmacy",      "factor_type": "Medication",  "description": "More than 5 medications prescribed",       "rs_id": "RS001"},
        {"rf_id": "RF003", "factor_name": "Low Hemoglobin",    "factor_type": "Lab Result",  "description": "Hemoglobin below 12 g/dL at discharge",    "rs_id": "RS003"},
        {"rf_id": "RF004", "factor_name": "Prior ED Visit",    "factor_type": "Utilization", "description": "ED visit within 6 months before admission","rs_id": "RS002"},
        {"rf_id": "RF005", "factor_name": "Uncontrolled COPD", "factor_type": "Comorbidity", "description": "COPD with FEV1 < 50%",                     "rs_id": "RS007"},
        {"rf_id": "RF006", "factor_name": "High BUN",          "factor_type": "Lab Result",  "description": "Blood urea nitrogen > 25 mg/dL",           "rs_id": "RS005"},
        {"rf_id": "RF007", "factor_name": "No Follow-up Plan", "factor_type": "Care Gap",    "description": "Discharged without follow-up appointment", "rs_id": "RS004"},
        {"rf_id": "RF008", "factor_name": "Social Isolation",  "factor_type": "Social",      "description": "Patient lives alone, no caregiver",        "rs_id": "RS005"},
    ]
    _upsert_many(db.risk_factors, factors, "rf_id")

    interventions = [
        {"intervention_id": "IN001", "intervention_name": "Medication Reconciliation", "type": "Clinical",        "start_date": "2025-01-18", "end_date": "2025-01-25", "status": "Completed", "rr_ids": ["RR001"],          "rf_ids": ["RF002"]},
        {"intervention_id": "IN002", "intervention_name": "Follow-up Appointment",     "type": "Outpatient",      "start_date": "2025-01-20", "end_date": None,          "status": "Ongoing",   "rr_ids": ["RR001", "RR003"], "rf_ids": ["RF001", "RF003"]},
        {"intervention_id": "IN003", "intervention_name": "Patient Education",         "type": "Preventive",      "start_date": "2025-03-09", "end_date": "2025-03-15", "status": "Completed", "rr_ids": ["RR003"],          "rf_ids": ["RF003"]},
        {"intervention_id": "IN004", "intervention_name": "Pulmonary Rehab",           "type": "Clinical",        "start_date": "2025-05-15", "end_date": "2025-06-15", "status": "Ongoing",   "rr_ids": ["RR007"],          "rf_ids": ["RF005"]},
        {"intervention_id": "IN005", "intervention_name": "Social Worker Referral",    "type": "Social",          "start_date": "2025-04-13", "end_date": "2025-04-30", "status": "Completed", "rr_ids": ["RR005"],          "rf_ids": ["RF008"]},
        {"intervention_id": "IN006", "intervention_name": "Dietitian Consultation",    "type": "Preventive",      "start_date": "2025-03-20", "end_date": "2025-04-01", "status": "Completed", "rr_ids": ["RR004"],          "rf_ids": ["RF007"]},
    ]
    _upsert_many(db.interventions, interventions, "intervention_id")

    strategies = [
        {"strategy_id": "PS001", "strategy_name": "Transitional Care Program",  "category": "Post-Discharge",    "description": "Structured follow-up within 7 days of discharge", "rr_ids": ["RR001", "RR003", "RR005"]},
        {"strategy_id": "PS002", "strategy_name": "Chronic Disease Management", "category": "Outpatient",        "description": "Regular monitoring for chronic conditions",        "rr_ids": ["RR001", "RR007"]},
        {"strategy_id": "PS003", "strategy_name": "Remote Patient Monitoring",  "category": "Telehealth",        "description": "Daily vitals tracking via mobile app",             "rr_ids": ["RR005", "RR007"]},
        {"strategy_id": "PS004", "strategy_name": "Care Coordination Program",  "category": "Multidisciplinary", "description": "Team-based care with nurse navigator",             "rr_ids": ["RR003", "RR004"]},
    ]
    _upsert_many(db.prevention_strategies, strategies, "strategy_id")

    metrics = [
        {"report_id": "QM001", "strategy_id": "PS001", "metric_name": "30-Day Readmission Rate",   "value": 18.5, "reporting_period": "Q1-2025", "report_point": "Hospital-wide",    "indicator": "Decrease"},
        {"report_id": "QM002", "strategy_id": "PS001", "metric_name": "Follow-up Compliance Rate", "value": 72.3, "reporting_period": "Q1-2025", "report_point": "Cardiology",        "indicator": "Increase"},
        {"report_id": "QM003", "strategy_id": "PS002", "metric_name": "Preventable Readmissions",  "value": 9.1,  "reporting_period": "Q1-2025", "report_point": "Hospital-wide",    "indicator": "Decrease"},
        {"report_id": "QM004", "strategy_id": "PS003", "metric_name": "Patient Engagement Score",  "value": 84.0, "reporting_period": "Q2-2025", "report_point": "Telehealth",        "indicator": "Increase"},
        {"report_id": "QM005", "strategy_id": "PS004", "metric_name": "Care Plan Adherence",       "value": 67.5, "reporting_period": "Q2-2025", "report_point": "Multidisciplinary", "indicator": "Increase"},
        {"report_id": "QM006", "strategy_id": "PS001", "metric_name": "30-Day Readmission Rate",   "value": 15.2, "reporting_period": "Q2-2025", "report_point": "Hospital-wide",    "indicator": "Decrease"},
    ]
    _upsert_many(db.quality_metrics, metrics, "report_id")

    print("✅ Seed data inserted successfully.")


def _upsert_many(collection, docs, key_field):
    for doc in docs:
        collection.update_one(
            {key_field: doc[key_field]},
            {"$set": doc},
            upsert=True
        )


if __name__ == "__main__":
    seed()
