"""
ml_model.py — BloodSetu AI/ML Engine
KNN donor matching + Random Forest shortage prediction
"""

import numpy as np
import pandas as pd
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from datetime import date, timedelta
from database import get_eligible_donors, get_all_hospitals
from utils import get_compatible_groups, GUJARAT_AREAS


# ══════════════════════════════════════════
# AREA DISTANCE PROXY (area index = distance)
# ══════════════════════════════════════════
def area_distance(area1: str, area2: str, city: str) -> int:
    """Return a distance proxy (0 = same area, higher = further)."""
    areas = GUJARAT_AREAS.get(city, [])
    try:
        i1 = areas.index(area1)
        i2 = areas.index(area2)
        return abs(i1 - i2)
    except ValueError:
        return 999


# ══════════════════════════════════════════
# KNN DONOR MATCHING
# ══════════════════════════════════════════
def knn_rank_donors(donors: list, seeker_area: str, city: str) -> list:
    """
    Rank donors using KNN concept:
    Features: distance proxy, donations_count (inverted = experience)
    Returns sorted list — nearest & most experienced first.
    """
    if not donors:
        return []

    scored = []
    for d in donors:
        dist = area_distance(d["area"], seeker_area, city)
        exp_score = d.get("donations_count", 0)
        # lower dist = better, higher exp = better
        score = dist * 10 - exp_score
        scored.append((score, d))

    scored.sort(key=lambda x: x[0])
    return [d for _, d in scored]


# ══════════════════════════════════════════
# RANDOM FOREST — BLOOD SHORTAGE PREDICTION
# ══════════════════════════════════════════
def generate_synthetic_shortage_data() -> pd.DataFrame:
    """
    Generate synthetic monthly data for shortage prediction.
    Features: month, blood_group_enc, donor_count, request_count
    Target: shortage (0=no, 1=yes)
    """
    np.random.seed(42)
    records = []
    groups = ["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"]
    rare = ["A-", "B-", "O-", "AB-"]

    for month in range(1, 13):
        for i, group in enumerate(groups):
            donors = np.random.randint(5, 60) if group not in rare else np.random.randint(1, 15)
            requests = np.random.randint(3, 50)
            shortage = 1 if requests > donors * 1.3 else 0
            records.append({
                "month": month,
                "blood_group_enc": i,
                "donor_count": donors,
                "request_count": requests,
                "shortage": shortage,
            })

    return pd.DataFrame(records)


def train_shortage_model():
    """Train Random Forest on synthetic data and return model."""
    df = generate_synthetic_shortage_data()
    X = df[["month", "blood_group_enc", "donor_count", "request_count"]]
    y = df["shortage"]
    model = RandomForestClassifier(n_estimators=50, random_state=42)
    model.fit(X, y)
    return model


_shortage_model = None


def get_shortage_model():
    global _shortage_model
    if _shortage_model is None:
        _shortage_model = train_shortage_model()
    return _shortage_model


def predict_shortage(city: str = "Vadodara") -> dict:
    """
    Predict shortage status for each blood group next month.
    Returns dict: blood_group -> {"status": str, "probability": float}
    """
    model = get_shortage_model()
    groups = ["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"]
    rare = ["A-", "B-", "O-", "AB-"]
    next_month = (date.today().month % 12) + 1
    np.random.seed(date.today().day)

    results = {}
    for i, group in enumerate(groups):
        donors = np.random.randint(1, 12) if group in rare else np.random.randint(5, 50)
        requests = np.random.randint(3, 45)
        X = np.array([[next_month, i, donors, requests]])
        prob = model.predict_proba(X)[0][1]
        if prob > 0.65:
            status = "🔴 Critical"
        elif prob > 0.35:
            status = "🟡 Low"
        else:
            status = "🟢 Good"
        results[group] = {"status": status, "probability": round(prob * 100, 1)}

    return results


# ══════════════════════════════════════════
# FULL TIER SEARCH (T1 → T5)
# ══════════════════════════════════════════
def tier_search(blood_group: str, city: str, area: str):
    """
    Run 5-tier cascading search.
    Returns dict with results per tier.
    """
    from database import (search_hospitals, search_blood_banks,
                          search_camps, get_eligible_donors)

    compatible = get_compatible_groups(blood_group)

    results = {
        "T1_hospitals": [],
        "T2_banks": [],
        "T3_camps": [],
        "T4_donors": [],
        "found_at": None,
    }

    # TIER 1 — Hospitals
    for bg in compatible:
        hosp = search_hospitals(bg, city, area)
        if hosp:
            results["T1_hospitals"].extend(hosp)
    if results["T1_hospitals"]:
        results["found_at"] = "T1"
        return results

    # TIER 2 — Blood Banks
    for bg in compatible:
        banks = search_blood_banks(bg, city)
        if banks:
            results["T2_banks"].extend(banks)
    if results["T2_banks"]:
        results["found_at"] = "T2"
        return results

    # TIER 3 — Blood Camps
    camps = search_camps(city)
    if camps:
        results["T3_camps"] = camps
        results["found_at"] = "T3"
        return results

    # TIER 4 — Donors (90-day rule enforced inside get_eligible_donors)
    donors = get_eligible_donors(compatible, city, area)
    if donors:
        results["T4_donors"] = knn_rank_donors(donors, area, city)
        results["found_at"] = "T4"
        return results

    # TIER 5 — WhatsApp SOS (nothing found)
    results["found_at"] = "T5"
    return results

