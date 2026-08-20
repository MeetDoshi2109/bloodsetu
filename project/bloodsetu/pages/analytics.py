"""
pages/analytics.py — BloodSetu Analytics Dashboard
ML shortage prediction, charts, trends, platform stats
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from database import (get_platform_stats, get_all_donors_daata_wall,
                      get_all_hospitals, get_all_blood_banks)
from ml_model import predict_shortage
from utils import ALL_BLOOD_GROUPS


def show():
    st.markdown("""
    <div class='sec-header'>📊 Analytics Dashboard</div>
    <p class='sec-sub'>Live blood availability, ML shortage predictions and platform stats</p>
    """, unsafe_allow_html=True)

    stats = get_platform_stats()

    # ── TOP STATS ──────────────────────────────────────────
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("🩸 Donors", stats["donors"])
    c2.metric("🏥 Hospitals", stats["hospitals"])
    c3.metric("🏦 Blood Banks", stats["banks"])
    c4.metric("🏕️ Camps", stats["camps"])
    c5.metric("❤️ Donations", stats["donations"])

    if stats["active_sos"] > 0:
        st.error(f"🚨 {stats['active_sos']} active SOS request(s) right now!")

    st.markdown("---")

    # ── ML SHORTAGE PREDICTION ──────────────────────────────
    st.markdown("### 🤖 AI Blood Shortage Forecast (Next Month)")
    st.caption(
        "Powered by Random Forest ML model — predicts which blood groups "
        "may run short based on donation and request patterns."
    )

    shortage = predict_shortage()
    groups   = list(shortage.keys())
    probs    = [shortage[g]["probability"] for g in groups]
    statuses = [shortage[g]["status"] for g in groups]

    colors = []
    for s in statuses:
        if "Critical" in s:
            colors.append("#e74c3c")
        elif "Low" in s:
            colors.append("#f0c040")
        else:
            colors.append("#2ecc71")

    fig = go.Figure(go.Bar(
        x=groups,
        y=probs,
        marker_color=colors,
        text=[s for s in statuses],
        textposition="outside",
        hovertemplate="<b>%{x}</b><br>Shortage risk: %{y:.1f}%<extra></extra>"
    ))
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="rgba(255,255,255,0.7)", family="Poppins"),
        yaxis=dict(
            title="Shortage Risk %",
            gridcolor="rgba(255,255,255,0.05)",
            range=[0, 120]
        ),
        xaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
        margin=dict(t=30, b=10, l=0, r=0),
        height=320,
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)

    # Status grid
    cols = st.columns(8)
    for col, g in zip(cols, groups):
        s = shortage[g]["status"]
        color = "#e74c3c" if "Critical" in s else "#f0c040" if "Low" in s else "#2ecc71"
        col.markdown(f"""
        <div style='text-align:center;background:rgba(255,255,255,0.04);
        border:1px solid rgba(192,57,43,0.2);border-radius:10px;padding:10px 4px'>
          <div style='font-size:16px;font-weight:700;color:white'>{g}</div>
          <div style='font-size:18px;margin:4px 0'>{s.split()[0]}</div>
          <div style='font-size:10px;color:{color}'>{shortage[g]["probability"]}%</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # ── DONOR DISTRIBUTION ──────────────────────────────────
    st.markdown("### 🩸 Donors by Blood Group")
    donors = get_all_donors_daata_wall()

    if donors:
        from collections import Counter
        group_counts = Counter(d["blood_group"] for d in donors)
        all_counts = {g: group_counts.get(g, 0) for g in ALL_BLOOD_GROUPS}

        fig2 = px.pie(
            names=list(all_counts.keys()),
            values=list(all_counts.values()),
            color_discrete_sequence=["#c0392b","#e74c3c","#7b241c","#922b21",
                                     "#f0c040","#d4a017","#2ecc71","#27ae60"],
            hole=0.4,
        )
        fig2.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="rgba(255,255,255,0.7)", family="Poppins"),
            margin=dict(t=10, b=10, l=0, r=0),
            height=300,
            legend=dict(font=dict(color="rgba(255,255,255,0.6)")),
        )
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("No donor data available yet.")

    st.markdown("---")

    # ── HOSPITAL COVERAGE ───────────────────────────────────
    st.markdown("### 🏥 Hospital Coverage by City")
    hospitals = get_all_hospitals()

    if hospitals:
        from collections import Counter
        city_counts = Counter(h["city"] for h in hospitals)

        fig3 = go.Figure(go.Bar(
            x=list(city_counts.keys()),
            y=list(city_counts.values()),
            marker_color="#c0392b",
            hovertemplate="<b>%{x}</b><br>Hospitals: %{y}<extra></extra>"
        ))
        fig3.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="rgba(255,255,255,0.7)", family="Poppins"),
            yaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
            xaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
            margin=dict(t=10, b=10, l=0, r=0),
            height=260,
        )
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("No hospital data available yet.")

    st.markdown("---")

    # ── ML MODEL INFO ───────────────────────────────────────
    st.markdown("### 🤖 ML Models Used in BloodSetu")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class='bs-card'>
          <p style='font-weight:700;color:#e74c3c;margin:0 0 6px'>
          🎯 KNN (K-Nearest Neighbors)</p>
          <p style='font-size:12px;color:rgba(255,255,255,0.6);margin:0'>
          Used to rank and match eligible donors by proximity to the seeker.
          Features: area distance, donation experience. K=3.</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class='bs-card'>
          <p style='font-weight:700;color:#e74c3c;margin:0 0 6px'>
          🌲 Random Forest</p>
          <p style='font-size:12px;color:rgba(255,255,255,0.6);margin:0'>
          Predicts blood shortage probability per group for next month.
          Trained on synthetic donation + request pattern data.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div class='bs-footer'>
      🤖 AI predictions are based on synthetic data for academic demonstration.
      In production, real donation records would be used.
    </div>
    """, unsafe_allow_html=True)
    