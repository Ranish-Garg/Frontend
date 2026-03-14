"""
F4 - Readmission Risk Analysis Database
UI module — plugs into patient_dashboard.py show_module_detail()
"""

import streamlit as st
from .api import (
    get_all_patients, get_all_readmissions, get_high_risk_patients,
    get_risk_category_distribution, get_preventable_readmissions,
    get_full_readmission_report, get_readmission_summary_stats,
    get_all_strategies, get_metrics_by_strategy
)
from .db import get_db


def readmission_module_ui():
    st.markdown("# 📋 Readmission Risk Analysis Database")
    st.caption("Readmission prediction — F4")
    st.divider()

    tab = st.radio(
        "Navigation",
        ["🏠 Home", "🔗 ER Diagram", "📋 Tables", "🔍 Queries", "⚡ Triggers", "📊 Output"],
        horizontal=True,
        label_visibility="collapsed"
    )
    st.divider()

    if tab == "🏠 Home":
        _tab_home()
    elif tab == "🔗 ER Diagram":
        _tab_er()
    elif tab == "📋 Tables":
        _tab_tables()
    elif tab == "🔍 Queries":
        _tab_queries()
    elif tab == "⚡ Triggers":
        _tab_triggers()
    elif tab == "📊 Output":
        _tab_output()


# ── HOME ──────────────────────────────────────────────────────────────────────
def _tab_home():
    try:
        stats = get_readmission_summary_stats()
    except Exception:
        stats = {"total_readmissions": 0, "preventable": 0, "ar_flagged": 0,
                 "avg_length_of_stay": 0, "risk_distribution": []}

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Readmissions", stats["total_readmissions"])
    c2.metric("Preventable", stats["preventable"])
    c3.metric("AR Flagged", stats["ar_flagged"])
    c4.metric("Avg Length of Stay", f"{stats['avg_length_of_stay']} days")

    st.divider()
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Input Entities")
        st.success("1️⃣ Patient Demographics")
        st.success("2️⃣ Admission & Discharge Records")
        st.success("3️⃣ Risk Factor Data")
        st.success("4️⃣ Clinical Interventions")

    with col2:
        st.markdown("### Output Entities")
        st.success("1️⃣ Risk Score & Category")
        st.success("2️⃣ Readmission Prediction")
        st.success("3️⃣ Prevention Strategy")
        st.success("4️⃣ Quality Metrics Report")

    st.divider()
    st.markdown("### Risk Category Distribution")
    dist = stats.get("risk_distribution", [])
    if dist:
        for d in dist:
            st.markdown(f"**{d['_id']}** — {d['count']} patients")
    else:
        st.info("No risk score data yet.")


# ── ER DIAGRAM ────────────────────────────────────────────────────────────────
def _tab_er():
    st.markdown("### Entity Relationship Diagram")
    st.image("src/modules/Readmission_Risk_Analysis_Database/er_diagram_view.png", caption="ER Diagram — Readmission Risk Analysis")


# ── TABLES ────────────────────────────────────────────────────────────────────
def _tab_tables():
    st.markdown("### Database Collections (MongoDB)")

    db = get_db()
    collections = [
        ("patients",              "Patient demographics and insurance info"),
        ("risk_models",           "Scoring models (LACE, HOSPITAL)"),
        ("readmissions",          "Admission/discharge and readmission events"),
        ("risk_scores",           "Computed risk scores per readmission"),
        ("risk_factors",          "Clinical factors contributing to risk"),
        ("interventions",         "Clinical interventions applied"),
        ("prevention_strategies", "Post-discharge prevention plans"),
        ("quality_metrics",       "Outcome and performance metrics"),
    ]

    names, descs, counts = [], [], []
    for col, desc in collections:
        names.append(col)
        descs.append(desc)
        try:
            counts.append(db[col].count_documents({}))
        except Exception:
            counts.append("—")

    st.table({"Collection": names, "Description": descs, "Records": counts})

    st.divider()
    selected = st.selectbox("Browse collection", [c[0] for c in collections])
    if st.button("Load Records"):
        try:
            docs = list(db[selected].find({}, {"_id": 0}).limit(10))
            if docs:
                st.dataframe(docs)
            else:
                st.info("No records found.")
        except Exception as e:
            st.error(f"Error: {e}")


# ── QUERIES ───────────────────────────────────────────────────────────────────
def _tab_queries():
    st.markdown("### Sample Queries")

    query = st.selectbox("Select a query", [
        "All Patients",
        "All Readmissions",
        "High Risk Patients",
        "Preventable Readmissions",
        "Full Report for a Readmission",
        "Risk Category Distribution",
    ])

    if query == "All Patients":
        st.code("db.patients.find({}, {_id: 0})", language="javascript")
        if st.button("▶️ Run"):
            st.dataframe(get_all_patients())

    elif query == "All Readmissions":
        st.code("db.readmissions.find({}, {_id: 0})", language="javascript")
        if st.button("▶️ Run"):
            st.dataframe(get_all_readmissions())

    elif query == "High Risk Patients":
        st.code('db.risk_scores.find({risk_category: "High"}, {_id: 0})', language="javascript")
        if st.button("▶️ Run"):
            data = get_high_risk_patients()
            for row in data:
                st.json(row)

    elif query == "Preventable Readmissions":
        st.code("db.readmissions.find({preventable_flag: true}, {_id: 0})", language="javascript")
        if st.button("▶️ Run"):
            st.dataframe(get_preventable_readmissions())

    elif query == "Full Report for a Readmission":
        rr_id = st.text_input("Enter RR ID (e.g. RR001)")
        st.code("db.readmissions + risk_scores + risk_factors + interventions + strategies", language="javascript")
        if st.button("▶️ Run") and rr_id:
            result = get_full_readmission_report(rr_id)
            if result:
                st.json(result)
            else:
                st.warning("No record found.")

    elif query == "Risk Category Distribution":
        st.code("""
db.risk_scores.aggregate([
  { $group: { _id: "$risk_category", count: { $sum: 1 } } },
  { $sort: { count: -1 } }
])""", language="javascript")
        if st.button("▶️ Run"):
            st.dataframe(get_risk_category_distribution())


# ── TRIGGERS ──────────────────────────────────────────────────────────────────
def _tab_triggers():
    st.markdown("### Trigger-Like Logic (MongoDB Application Layer)")

    st.markdown("**Trigger 1 — Auto Risk Score on New Readmission**")
    st.code("""
# Fires when add_readmission() is called
def _trigger_risk_score(readmission):
    los = readmission.get("length_of_stay", 0)
    if los > 7:
        category, score = "High", 8.0
    elif los >= 4:
        category, score = "Medium", 5.0
    else:
        category, score = "Low", 2.5

    db.risk_scores.insert_one({
        "rs_id": f"RS_AUTO_{readmission['rr_id']}",
        "patient_id": readmission["patient_id"],
        "score_value": score,
        "risk_category": category,
        "risk_calculation_date": today
    })
""", language="python")

    st.divider()
    st.markdown("**Trigger 2 — Flag Preventable Readmission**")
    st.code("""
# If readmission occurs within 30 days of discharge → preventable_flag = True
def check_preventable(discharge_date, readmission_date):
    delta = (readmission_date - discharge_date).days
    return delta <= 30
""", language="python")

    st.divider()
    st.markdown("**Trigger 3 — Intervention Status Update**")
    st.code("""
# When end_date is reached, auto-set status to "Completed"
db.interventions.update_many(
    { "end_date": { "$lte": today }, "status": "Ongoing" },
    { "$set": { "status": "Completed" } }
)
""", language="python")


# ── OUTPUT ────────────────────────────────────────────────────────────────────
def _tab_output():
    st.markdown("### Live Output from MongoDB Atlas")

    st.markdown("#### High Risk Patients")
    try:
        high_risk = get_high_risk_patients()
        if high_risk:
            for row in high_risk:
                p = row["patient"]
                s = row["risk_score"]
                col1, col2, col3 = st.columns(3)
                col1.markdown(f"**{p['first_name']} {p['last_name']}**")
                col2.markdown(f"Score: `{s['score_value']}`")
                col3.markdown(f"🔴 {s['risk_category']}")
        else:
            st.info("No high risk patients found.")
    except Exception as e:
        st.error(f"DB Error: {e}")

    st.divider()
    st.markdown("#### Prevention Strategies")
    try:
        strategies = get_all_strategies()
        if strategies:
            for s in strategies:
                st.markdown(f"- **{s['strategy_name']}** ({s.get('category', '')}): {s.get('description', '')}")
        else:
            st.info("No strategies found.")
    except Exception as e:
        st.error(f"DB Error: {e}")

    st.divider()
    st.markdown("#### Quality Metrics")
    try:
        db = get_db()
        metrics = list(db.quality_metrics.find({}, {"_id": 0}))
        if metrics:
            st.dataframe(metrics)
        else:
            st.info("No metrics found.")
    except Exception as e:
        st.error(f"DB Error: {e}")
