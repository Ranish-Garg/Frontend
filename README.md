# F4 — Readmission Risk Analysis Database

**Module 34 | Category F: Case-Based Clinical Decision Support**  
**Student:** **Prathamesh S. Vispute | 24JE0674** 

**Ranish Garg | 24JE0682** 

**Poka Sireesha | 24JE0671**        
**Database:** MongoDB Atlas  

---

## Overview

This module predicts the risk of hospital readmission for patients using clinical data.
It selects a scoring model based on patient inputs, calculates a risk score, stores results
in MongoDB Atlas, and automatically triggers interventions and prevention strategies when
the score exceeds a threshold.

---

## Database Collections (8 total)

| Collection | Description |
|---|---|
| `patients` | Patient demographics, contact, insurance info |
| `risk_models` | Scoring models — LACE, HOSPITAL, BOOST |
| `readmissions` | Admission/discharge records, chronic type, flags |
| `risk_scores` | Computed risk scores linked to readmissions |
| `risk_factors` | Clinical factors contributing to risk |
| `interventions` | Triggered interventions per readmission |
| `prevention_strategies` | Post-discharge prevention plans |
| `quality_metrics` | Outcome metrics per strategy and period |

---

## ER Diagram Entities & Relationships

- `Patient` has many `Readmissions` (1:N)
- `Patient` generates many `Risk Scores` (1:N)
- `Risk Model` is used to calculate `Risk Score` (M:N via Readmission)
- `Risk Score` is associated with many `Risk Factors` (1:N)
- `Readmission` needs many `Interventions` (M:N)
- `Readmission` applies to many `Prevention Strategies` (M:N)
- `Prevention Strategy` is measured by `Quality Metrics` (1:N)

---

## Full Pipeline

```
Patient + Readmission Input
        ↓
Model Selection (LACE / HOSPITAL / BOOST)
        ↓
Risk Score Calculation
        ↓
Save to MongoDB Atlas
        ↓
Score ≥ Threshold?
   ├── High (≥7.0) → Trigger "Urgent Care Coordination" + Post-Discharge Strategy
   ├── Medium (≥4.0) → Trigger "Follow-up Appointment" + Outpatient Strategy
   └── Low (<4.0) → No intervention
        ↓
Display Results to User
```

---

## Model Selection Logic

| Condition | Model Selected |
|---|---|
| Oncology diagnosis OR lab abnormality | HOSPITAL Score (RM002) |
| Length of stay < 4 days | BOOST Score (RM003) |
| Default | LACE Score (RM001) |

---

## Scoring Formulas

**LACE Score**
```
L = min(LOS, 7)
A = 3 if acute else 0
C = min(comorbidities × 2, 5)
E = min(ED_visits × 1.5, 4)
Score = L + A + C + E
```

**HOSPITAL Score**
```
Score = min(LOS × 0.5, 3) + (comorbidities × 1.5) + (ED_visits × 1.0)
```

**BOOST Score**
```
Score = (LOS × 0.3) + (comorbidities × 1.0) + (ED_visits × 0.5)
```

---

## Trigger Logic

| Trigger | Condition | Action |
|---|---|---|
| Auto Risk Score | New readmission added | Calculate and save score |
| Preventable Flag | Readmission within 30 days of discharge | Set `preventable_flag = True` |
| Intervention | Score ≥ 4.0 (Medium/High) | Insert intervention record |
| Prevention Strategy | Score ≥ 4.0 | Assign strategy from DB |
| Intervention Status | End date reached | Auto-set status to Completed |

---

## File Structure

```
src/modules/Readmission_Risk_Analysis_Database/
├── __init__.py
├── db.py           — MongoDB Atlas connection + schema validation for all 8 collections
├── seed.py         — One-time script to populate mock data
├── api.py          — CRUD + full pipeline logic + trigger functions
├── queries.py      — Read-only analytical queries and aggregations
├── ui.py           — Streamlit UI with 7 tabs
├── er_diagram_view.png
└── README.md
```

---

## UI Tabs

| Tab | Description |
|---|---|
| 🏠 Home | Summary stats — total readmissions, preventable count, risk distribution |
| ➕ New Analysis | Select patient + readmission → run full pipeline → see results |
| 🔗 ER Diagram | Hand-drawn ER diagram for the module |
| 📋 Tables | All 8 collections with record counts, browse any collection |
| 🔍 Queries | Run sample MongoDB queries with live Atlas results |
| ⚡ Triggers | View all 5 trigger logic implementations |
| 📊 Output | Live high risk patients, active interventions, strategies, metrics |

---

## Setup

**1. Install dependencies**
```bash
pip install -r requirements.txt
```

**2. Configure Atlas connection**  
Create a `.env` file in the project root:
```
MONGO_PASSWORD=your_atlas_password
```

**3. Seed the database**
```bash
python -m src.modules.Readmission_Risk_Analysis_Database.seed
```

**4. Run the app**
```bash
streamlit run app.py
```

---

## Sample Data

- 8 patients with demographics and insurance info
- 3 risk models (LACE, HOSPITAL, BOOST)
- 8 readmission records across various chronic conditions
- 8 risk scores (High / Medium / Low)
- 8 risk factors across comorbidity, lab, medication, social categories
- 6 interventions (clinical, outpatient, preventive, social)
- 4 prevention strategies (post-discharge, outpatient, telehealth, multidisciplinary)
- 6 quality metrics across Q1 and Q2 2025
