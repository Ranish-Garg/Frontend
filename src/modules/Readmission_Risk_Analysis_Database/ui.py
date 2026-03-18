"""
F4 - Readmission Risk Analysis Database
UI module — plugs into patient_dashboard.py show_module_detail()
"""

import streamlit as st
from .api import (
    get_all_patients, get_all_readmissions, get_high_risk_patients,
    get_risk_category_distribution, get_preventable_readmissions,
    get_full_readmission_report, get_readmission_summary_stats,
    get_all_strategies, get_metrics_by_strategy, get_all_models,
    run_pipeline
)
from .db import get_db


def readmission_module_ui():
    st.markdown("# 📋 Readmission Risk Analysis Database")
    st.caption("Readmission prediction — F4")
    st.divider()

    tab = st.radio(
        "Navigation",
        ["🏠 Home", "➕ New Analysis", "� ER Diagram", "📋 Tables", "🔍 Queries", "⚡ Triggers", "📊 Output"],
        horizontal=True,
        label_visibility="collapsed"
    )
    st.divider()

    if tab == "🏠 Home":
        _tab_home()
    elif tab == "➕ New Analysis":
        _tab_pipeline()
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
            label = d["_id"]
            color = "🔴" if label == "High" else "🟡" if label == "Medium" else "🟢"
            st.markdown(f"{color} **{label}** — {d['count']} patients")
    else:
        st.info("No risk score data yet.")


# ── PIPELINE FORM ─────────────────────────────────────────────────────────────
def _tab_pipeline():
    st.markdown("### New Readmission Risk Analysis")
    st.caption("Select a patient and their readmission record to calculate risk score and trigger interventions.")

    db = get_db()

    # Patient selection
    patients = get_all_patients()
    if not patients:
        st.warning("No patients in database.")
        return

    patient_options = {f"{p['patient_id']} — {p['first_name']} {p['last_name']}": p["patient_id"] for p in patients}
    selected_label = st.selectbox("Select Patient", list(patient_options.keys()))
    patient_id = patient_options[selected_label]

    # Load readmissions for selected patient
    readmissions = list(db.readmissions.find({"patient_id": patient_id}, {"_id": 0}))
    if not readmissions:
        st.info("No readmission records found for this patient.")
        return

    rr_options = {f"{r['rr_id']} — {r['admission_date']} ({r['type_chronic']})": r for r in readmissions}
    selected_rr_label = st.selectbox("Select Readmission Record", list(rr_options.keys()))
    rr = rr_options[selected_rr_label]

    # Show the record details
    st.divider()
    st.markdown("#### Readmission Details")
    col1, col2, col3 = st.columns(3)
    col1.metric("Admission Date", rr["admission_date"])
    col2.metric("Discharge Date", rr["discharge_date"])
    col3.metric("Length of Stay", f"{rr['length_of_stay']} days")

    col4, col5, col6 = st.columns(3)
    col4.metric("Condition", rr["type_chronic"])
    col5.metric("Status", rr["status_to_chronic"])
    col6.metric("AR Flag", "Yes" if rr["ar_flag"] else "No")

    # Additional clinical inputs not stored in readmission
    st.divider()
    st.markdown("#### Additional Clinical Indicators")
    col7, col8 = st.columns(2)
    with col7:
        num_comorbidities   = st.slider("Number of Comorbidities", 0, 10, 1)
        prior_ed_visits     = st.slider("Prior ED Visits (last 6 months)", 0, 10, 0)
    with col8:
        has_oncology        = st.checkbox("Oncology Diagnosis")
        has_lab_abnormality = st.checkbox("Lab Abnormality at Discharge")

    factor_options = [
        {"name": "Heart Failure",     "type": "Comorbidity",  "description": "Chronic heart failure diagnosis"},
        {"name": "Polypharmacy",      "type": "Medication",   "description": "More than 5 medications prescribed"},
        {"name": "Low Hemoglobin",    "type": "Lab Result",   "description": "Hemoglobin below 12 g/dL"},
        {"name": "Prior ED Visit",    "type": "Utilization",  "description": "ED visit within 6 months"},
        {"name": "Uncontrolled COPD", "type": "Comorbidity",  "description": "COPD with FEV1 < 50%"},
        {"name": "High BUN",          "type": "Lab Result",   "description": "Blood urea nitrogen > 25 mg/dL"},
        {"name": "No Follow-up Plan", "type": "Care Gap",     "description": "Discharged without follow-up"},
        {"name": "Social Isolation",  "type": "Social",       "description": "Patient lives alone"},
    ]
    selected_factor_names = st.multiselect("Select applicable risk factors", [f["name"] for f in factor_options])
    selected_factors = [f for f in factor_options if f["name"] in selected_factor_names]

    # Preview score
    st.divider()
    from .api import select_model, calculate_score, score_to_category, HIGH_RISK_THRESHOLD, MEDIUM_RISK_THRESHOLD
    los        = rr["length_of_stay"]
    is_acute   = rr["status_to_chronic"] == "Acute"
    model_id   = select_model(los, has_oncology, has_lab_abnormality)
    score      = calculate_score(model_id, los, num_comorbidities, prior_ed_visits, is_acute)
    category   = score_to_category(score)
    model_names = {"RM001": "LACE Score", "RM002": "HOSPITAL Score", "RM003": "BOOST Score"}
    color = "🔴" if category == "High" else "🟡" if category == "Medium" else "🟢"

    st.info(f"Model: **{model_names.get(model_id)}** | Estimated Score: **{score}** {color} **{category}**")
    if category == "High":
        st.warning("⚠️ High risk — intervention will be triggered automatically on submit.")
    elif category == "Medium":
        st.warning("⚠️ Medium risk — follow-up appointment will be scheduled on submit.")

    if st.button("🚀 Run Analysis & Save to Database", type="primary"):
        existing_score = db.risk_scores.find_one({"rr_id": rr["rr_id"]}, {"_id": 0})

        if existing_score:
            # Already analysed — show results nicely
            st.success(f"✅ Analysis for **{rr['rr_id']}**")
            st.divider()
            r1, r2, r3 = st.columns(3)
            r1.metric("Risk Score", existing_score["score_value"])
            r2.metric("Risk Category", existing_score["risk_category"])
            r3.metric("Model Used", model_names.get(existing_score["model_id"], existing_score["model_id"]))

            if rr.get("preventable_flag"):
                st.error("🚨 Flagged as PREVENTABLE (readmission within 30 days of last discharge)")

            # Show intervention
            intervention = db.interventions.find_one({"rr_ids": rr["rr_id"]}, {"_id": 0})
            if intervention:
                st.warning(f"⚡ Intervention: **{intervention['intervention_name']}** ({intervention['type']}) — Status: {intervention['status']}")
            else:
                st.success("✅ Low risk — no immediate intervention required.")

            # Show prevention strategy
            strategy = db.prevention_strategies.find_one({"rr_ids": rr["rr_id"]}, {"_id": 0})
            if not strategy:
                strategy = db.prevention_strategies.find_one({}, {"_id": 0})
            if strategy:
                st.info(f"🛡️ Prevention Strategy: **{strategy['strategy_name']}** ({strategy.get('category','')}) — {strategy.get('description','')}")

            # Show risk factors
            factors = list(db.risk_factors.find({"rs_id": existing_score["rs_id"]}, {"_id": 0}))
            if factors:
                st.divider()
                st.markdown("#### Risk Factors")
                for f in factors:
                    st.markdown(f"- **{f['factor_name']}** ({f['factor_type']}): {f.get('description','')}")
        else:
            try:
                result = run_pipeline(
                    patient_id=patient_id,
                    admission_date=rr["admission_date"],
                    discharge_date=rr["discharge_date"],
                    los=los,
                    type_chronic=rr["type_chronic"],
                    is_acute=is_acute,
                    ar_flag=rr["ar_flag"],
                    num_comorbidities=num_comorbidities,
                    prior_ed_visits=prior_ed_visits,
                    has_oncology=has_oncology,
                    has_lab_abnormality=has_lab_abnormality,
                    selected_factors=selected_factors
                )
                st.success(f"✅ Analysis complete! Readmission ID: **{result['rr_id']}**")
                st.divider()
                r1, r2, r3 = st.columns(3)
                r1.metric("Risk Score", result["score_value"])
                r2.metric("Risk Category", result["risk_category"])
                r3.metric("Model Used", model_names.get(result["model_used"], result["model_used"]))

                if result["preventable"]:
                    st.error("🚨 Flagged as PREVENTABLE (readmission within 30 days of last discharge)")

                if result["triggered_intervention"]:
                    i = result["triggered_intervention"]
                    st.warning(f"⚡ Intervention triggered: **{i['intervention_name']}** ({i['type']}) — Status: {i['status']}")
                else:
                    st.success("✅ Low risk — no immediate intervention required.")

                if result["assigned_strategy"]:
                    s = result["assigned_strategy"]
                    st.info(f"🛡️ Prevention Strategy: **{s['strategy_name']}** ({s.get('category','')}) — {s.get('description','')}")

                if selected_factors:
                    st.divider()
                    st.markdown("#### Risk Factors Recorded")
                    for f in selected_factors:
                        st.markdown(f"- **{f['name']}** ({f['type']}): {f.get('description','')}")

            except Exception as e:
                st.error(f"Error: {e}")


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
        ("risk_models",           "Scoring models (LACE, HOSPITAL, BOOST)"),
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
            st.dataframe(docs) if docs else st.info("No records found.")
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
            for row in get_high_risk_patients():
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
            st.json(result) if result else st.warning("No record found.")

    elif query == "Risk Category Distribution":
        st.code("""db.risk_scores.aggregate([
  { $group: { _id: "$risk_category", count: { $sum: 1 } } },
  { $sort: { count: -1 } }
])""", language="javascript")
        if st.button("▶️ Run"):
            st.dataframe(get_risk_category_distribution())


# ── TRIGGERS ──────────────────────────────────────────────────────────────────
def _tab_triggers():
    st.markdown("### Trigger-Like Logic (Application Layer)")

    st.markdown("**Trigger 1 — Model Selection based on Clinical Input**")
    st.code("""
def select_model(los, has_oncology, has_lab_abnormality):
    if has_oncology or has_lab_abnormality:
        return "RM002"  # HOSPITAL Score
    elif los < 4:
        return "RM003"  # BOOST Score
    else:
        return "RM001"  # LACE Score (default)
""", language="python")

    st.divider()
    st.markdown("**Trigger 2 — Auto Risk Score Calculation on New Readmission**")
    st.code("""
# LACE Score = L(LOS) + A(acuity) + C(comorbidities) + E(ED visits)
score = min(los,7) + (3 if is_acute else 0) + min(comorbidities*2,5) + min(ed_visits*1.5,4)
category = "High" if score >= 7 else "Medium" if score >= 4 else "Low"
db.risk_scores.insert_one({...score, category...})
""", language="python")

    st.divider()
    st.markdown("**Trigger 3 — Auto Intervention if Score ≥ Threshold**")
    st.code("""
if category in ("High", "Medium"):
    db.interventions.insert_one({
        "intervention_name": "Urgent Care Coordination",  # High
        "status": "Ongoing",
        "rr_ids": [rr_id]
    })
""", language="python")

    st.divider()
    st.markdown("**Trigger 4 — Preventable Flag (within 30 days)**")
    st.code("""
delta = (admission_date - last_discharge_date).days
preventable = delta <= 30
""", language="python")

    st.divider()
    st.markdown("**Trigger 5 — Auto Assign Prevention Strategy**")
    st.code("""
strategy = db.prevention_strategies.find_one({"category": "Post-Discharge"})
db.prevention_strategies.update_one(
    {"strategy_id": strategy["strategy_id"]},
    {"$addToSet": {"rr_ids": rr_id}}
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
                if not p:
                    continue
                col1, col2, col3 = st.columns(3)
                col1.markdown(f"**{p['first_name']} {p['last_name']}**")
                col2.markdown(f"Score: `{s['score_value']}`")
                col3.markdown(f"🔴 {s['risk_category']}")
        else:
            st.info("No high risk patients found.")
    except Exception as e:
        st.error(f"DB Error: {e}")

    st.divider()
    st.markdown("#### Active Interventions")
    try:
        db = get_db()
        interventions = list(db.interventions.find({"status": "Ongoing"}, {"_id": 0}))
        if interventions:
            st.dataframe(interventions)
        else:
            st.info("No active interventions.")
    except Exception as e:
        st.error(f"DB Error: {e}")

    st.divider()
    st.markdown("#### Prevention Strategies")
    try:
        for s in get_all_strategies():
            st.markdown(f"- **{s['strategy_name']}** ({s.get('category', '')}): {s.get('description', '')}")
    except Exception as e:
        st.error(f"DB Error: {e}")

    st.divider()
    st.markdown("#### Quality Metrics")
    try:
        db = get_db()
        metrics = list(db.quality_metrics.find({}, {"_id": 0}))
        st.dataframe(metrics) if metrics else st.info("No metrics found.")
    except Exception as e:
        st.error(f"DB Error: {e}")
