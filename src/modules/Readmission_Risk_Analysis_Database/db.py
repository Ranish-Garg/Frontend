"""
MongoDB connection and collection schema setup
for Readmission Risk Analysis (Module 34)
"""

import os
from dotenv import load_dotenv
from pymongo import MongoClient, ASCENDING
from pymongo.errors import CollectionInvalid

load_dotenv()
_password = os.environ.get("MONGO_PASSWORD", "")
MONGO_URI = f"mongodb+srv://ranishgarg2006_db_user:{_password}@cluster0.kxcxd7d.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
DB_NAME = "readmission_risk_db"

_client = None

def get_db():
    global _client
    if _client is None:
        _client = MongoClient(MONGO_URI)
    return _client[DB_NAME]


def setup_collections():
    """Create collections with JSON schema validation and indexes."""
    db = get_db()

    # ── PATIENTS ──────────────────────────────────────────────
    _create(db, "patients", {
        "bsonType": "object",
        "required": ["patient_id", "first_name", "last_name", "dob", "gender"],
        "properties": {
            "patient_id":   {"bsonType": "string"},
            "first_name":   {"bsonType": "string"},
            "last_name":    {"bsonType": "string"},
            "dob":          {"bsonType": "string"},   # ISO date string
            "age":          {"bsonType": "int"},
            "gender":       {"bsonType": "string", "enum": ["Male", "Female", "Other"]},
            "email":        {"bsonType": "string"},
            "contact":      {"bsonType": "string"},
            "insurance_id": {"bsonType": "string"},
            "mobile_no":    {"bsonType": "string"}
        }
    })
    db.patients.create_index([("patient_id", ASCENDING)], unique=True)

    # ── RISK MODEL ────────────────────────────────────────────
    _create(db, "risk_models", {
        "bsonType": "object",
        "required": ["model_id", "model_name", "version"],
        "properties": {
            "model_id":    {"bsonType": "string"},
            "model_name":  {"bsonType": "string"},
            "version":     {"bsonType": "string"},
            "description": {"bsonType": "string"}
        }
    })
    db.risk_models.create_index([("model_id", ASCENDING)], unique=True)

    # ── READMISSIONS ──────────────────────────────────────────
    _create(db, "readmissions", {
        "bsonType": "object",
        "required": ["rr_id", "patient_id", "admission_date", "discharge_date"],
        "properties": {
            "rr_id":               {"bsonType": "string"},
            "patient_id":          {"bsonType": "string"},   # FK → patients
            "prior_id":            {"bsonType": ["string", "null"]},   # previous admission ref
            "admission_date":      {"bsonType": "string"},
            "discharge_date":      {"bsonType": "string"},
            "length_of_stay":      {"bsonType": "int"},
            "readmission_date":    {"bsonType": ["string", "null"]},
            "status_to_chronic":   {"bsonType": "string"},
            "type_chronic":        {"bsonType": "string"},
            "ar_flag":             {"bsonType": "bool"},     # All-cause Readmission flag
            "preventable_flag":    {"bsonType": "bool"}
        }
    })
    db.readmissions.create_index([("rr_id", ASCENDING)], unique=True)
    db.readmissions.create_index([("patient_id", ASCENDING)])

    # ── RISK SCORES ───────────────────────────────────────────
    _create(db, "risk_scores", {
        "bsonType": "object",
        "required": ["rs_id", "patient_id", "rr_id", "model_id", "score_value", "risk_category"],
        "properties": {
            "rs_id":                  {"bsonType": "string"},
            "patient_id":             {"bsonType": "string"},   # FK → patients
            "rr_id":                  {"bsonType": "string"},   # FK → readmissions
            "model_id":               {"bsonType": "string"},   # FK → risk_models
            "score_value":            {"bsonType": "double"},
            "risk_category":          {"bsonType": "string", "enum": ["Low", "Medium", "High"]},
            "risk_calculation_date":  {"bsonType": "string"}
        }
    })
    db.risk_scores.create_index([("rs_id", ASCENDING)], unique=True)
    db.risk_scores.create_index([("patient_id", ASCENDING)])

    # ── RISK FACTORS ──────────────────────────────────────────
    _create(db, "risk_factors", {
        "bsonType": "object",
        "required": ["rf_id", "factor_name", "factor_type"],
        "properties": {
            "rf_id":        {"bsonType": "string"},
            "factor_name":  {"bsonType": "string"},
            "factor_type":  {"bsonType": "string"},
            "description":  {"bsonType": "string"},
            "rs_id":        {"bsonType": "string"}    # FK → risk_scores (associated_by)
        }
    })
    db.risk_factors.create_index([("rf_id", ASCENDING)], unique=True)

    # ── INTERVENTIONS ─────────────────────────────────────────
    _create(db, "interventions", {
        "bsonType": "object",
        "required": ["intervention_id", "intervention_name", "type"],
        "properties": {
            "intervention_id":   {"bsonType": "string"},
            "intervention_name": {"bsonType": "string"},
            "type":              {"bsonType": "string"},
            "start_date":        {"bsonType": "string"},
            "end_date":          {"bsonType": ["string", "null"]},
            "status":            {"bsonType": "string"},
            # M:N with readmissions and risk_factors stored as arrays
            "rr_ids":            {"bsonType": "array", "items": {"bsonType": "string"}},
            "rf_ids":            {"bsonType": "array", "items": {"bsonType": "string"}}
        }
    })
    db.interventions.create_index([("intervention_id", ASCENDING)], unique=True)

    # ── PREVENTION STRATEGIES ─────────────────────────────────
    _create(db, "prevention_strategies", {
        "bsonType": "object",
        "required": ["strategy_id", "strategy_name"],
        "properties": {
            "strategy_id":    {"bsonType": "string"},
            "strategy_name":  {"bsonType": "string"},
            "category":       {"bsonType": "string"},
            "description":    {"bsonType": "string"},
            # M:N with readmissions
            "rr_ids":         {"bsonType": "array", "items": {"bsonType": "string"}}
        }
    })
    db.prevention_strategies.create_index([("strategy_id", ASCENDING)], unique=True)

    # ── QUALITY METRICS ───────────────────────────────────────
    _create(db, "quality_metrics", {
        "bsonType": "object",
        "required": ["report_id", "metric_name", "value"],
        "properties": {
            "report_id":        {"bsonType": "string"},
            "strategy_id":      {"bsonType": "string"},   # FK → prevention_strategies
            "metric_name":      {"bsonType": "string"},
            "value":            {"bsonType": "double"},
            "reporting_period": {"bsonType": "string"},
            "report_point":     {"bsonType": "string"},
            "indicator":        {"bsonType": "string"}
        }
    })
    db.quality_metrics.create_index([("report_id", ASCENDING)], unique=True)

    print("✅ All collections created with schema validation.")


def _create(db, name, schema):
    """Create collection with validator, skip if already exists."""
    try:
        db.create_collection(name, validator={"$jsonSchema": schema})
    except CollectionInvalid:
        # Collection already exists — update validator
        db.command("collMod", name, validator={"$jsonSchema": schema})
