"""
views/home.py — BloodSetu Homepage
Split screen hero, search, stats, tier flow, Daata Wall preview, analytics strip
"""

import streamlit as st
import plotly.graph_objects as go
from database import (get_platform_stats, get_all_donors_daata_wall,
                      get_active_sos, expire_old_sos)
from utils import (GUJARAT_CITIES, get_areas, ALL_BLOOD_GROUPS, QUOTES, get_msg)
from ml_model import predict_shortage
import random


def show():
    # Expire old SOS first
    expire_old_sos()

    # ── URGENCY BANNER ──────────────────────────────────────
    active_sos = get_active_sos()
    if active_sos:
        sos = active_sos[0]
        st.markdown(f"""
        <div style='background:linear-gradient(90deg,#7b0d0d,#c0392b,#7b0d0d);
        padding:12px 24px;border-radius:12px;margin-bottom:20px;
        display:flex;align-items:center;gap:14px;box-shadow:0 8px 24px rgba(192,57,43,0.3)'>
          <span style='color:#ff6b6b;font-size:20px;animation:blink-tag 1s infinite'>🔴</span>
          <span style='color:white;font-size:13px;font-weight:600;letter-spacing:0.2px'>
            🚨 <b>CRITICAL EMERGENCY:</b> <span style='color:#f0c040;font-weight:700'>{sos["blood_group"]}</span> blood needed in
            <b>{sos["area"]}, {sos["city"]}</b> —
            Contact: <b style='color:#fff'>{sos["seeker_phone"]}</b>
          </span>
        </div>
        """, unsafe_allow_html=True)

    # ── HERO SPLIT SCREEN ───────────────────────────────────
    left, right = st.columns([1.1, 1], gap="large")

    with left:
        # Mascot SVG with smooth float animation
        st.markdown("""
        <div style='text-align:left;margin-bottom:12px'>
        <svg width='95' height='114' viewBox='0 0 80 96' fill='none'
             style='filter:drop-shadow(0 0 24px rgba(231,76,60,0.75))'>
          <path d='M40 8C40 8 8 44 8 64C8 82 22 88 40 88C58 88 72 82 72 64C72 44 40 8 40 8Z'
                fill='url(#mg)'/>
          <circle cx='30' cy='60' r='6' fill='white' opacity='.95'/>
          <circle cx='50' cy='60' r='6' fill='white' opacity='.95'/>
          <circle cx='31.5' cy='58.5' r='2.5' fill='#1a0505'/>
          <circle cx='51.5' cy='58.5' r='2.5' fill='#1a0505'/>
          <circle cx='32.5' cy='57.5' r='1' fill='white'/>
          <circle cx='52.5' cy='57.5' r='1' fill='white'/>
          <path d='M30 70 Q40 78 50 70' stroke='white' stroke-width='2.5'
                fill='none' stroke-linecap='round'/>
          <circle cx='24' cy='66' r='5' fill='#ff9999' opacity='.45'/>
          <circle cx='56' cy='66' r='5' fill='#ff9999' opacity='.45'/>
          <ellipse cx='28' cy='44' rx='7' ry='10'
                   fill='rgba(255,255,255,0.18)' transform='rotate(-20 28 44)'/>
          <defs>
            <linearGradient id='mg' x1='40' y1='8' x2='40' y2='88'
                            gradientUnits='userSpaceOnUse'>
              <stop offset='0%' stop-color='#ff4b4b'/>
              <stop offset='60%' stop-color='#e74c3c'/>
              <stop offset='100%' stop-color='#7b241c'/>
            </linearGradient>
          </defs>
        </svg></div>
        """, unsafe_allow_html=True)

        # Title & Quote
        q = random.choice(QUOTES)
        st.markdown(f"""
        <div style='margin-bottom:20px'>
          <h1 class='hero-title'>BloodSetu</h1>
          <p style='font-size:14px;color:rgba(255,255,255,0.5);margin-top:-6px;font-weight:500;letter-spacing:1px;text-transform:uppercase'>
            Gujarat's Smart AI Blood Network
          </p>
        </div>

        <div style='border-left:3px solid #e74c3c;padding-left:16px;margin-bottom:24px;background:rgba(255,255,255,0.02);padding-top:8px;padding-bottom:8px;border-radius:0 10px 10px 0'>
          <p style='font-family:"Playfair Display",serif;font-size:19px;
                    font-weight:700;color:white;margin:0;line-height:1.4'>
            "{q["en"]}"
          </p>
          <p style='font-size:13px;color:rgba(255,255,255,0.55);
                    margin:6px 0 0;font-style:italic'>
            "{q["gu"]}"
          </p>
        </div>
        """, unsafe_allow_html=True)

        # Live stats grid
        stats = get_platform_stats()
        c1, c2, c3 = st.columns(3)
        c1.metric("🩸 Donors", stats["donors"])
        c2.metric("🏥 Hospitals", stats["hospitals"])
        c3.metric("❤️ Donations", stats["donations"])

        st.markdown("<br>", unsafe_allow_html=True)

        # SOS button
        if st.button("🚨 EMERGENCY SOS REQUEST", use_container_width=True, key="home_sos_btn"):
            st.session_state["current_page"] = "Find Blood"
            st.rerun()

    with right:
        st.markdown("""
        <h2 style='font-family:"Playfair Display",serif;font-size:22px;
                   color:white;margin-bottom:4px;display:flex;align-items:center;gap:8px'>
          🔍 Quick Search
        </h2>
        <p style='font-size:12px;color:rgba(255,255,255,0.5);
                  margin-bottom:14px'>No login required for seekers. Find immediate help.</p>
        """, unsafe_allow_html=True)

        with st.form("home_search_form"):
            blood_group = st.selectbox(
                "🩸 Blood Group Needed",
                ALL_BLOOD_GROUPS,
                key="home_bg"
            )
            city = st.selectbox(
                "📍 City",
                GUJARAT_CITIES,
                key="home_city"
            )
            areas = get_areas(city)
            area = st.selectbox(
                "📍 Area in City",
                areas if areas else ["Select city first"],
                key="home_area"
            )
            confirm_loc = st.checkbox(
                f"✅ Confirm location: **{area}, {city}**",
                value=True,
                key="home_confirm"
            )
            urgency = st.radio(
                "⚡ Urgency Level",
                ["🔴 Critical", "🟡 Urgent", "🟢 Planned"],
                horizontal=True,
                key="home_urgency"
            )

            submitted = st.form_submit_button(
                "🔍 Search Gujarat Blood Network",
                use_container_width=True
            )

        if submitted:
            if not confirm_loc:
                st.warning("Please confirm your location before searching.")
            else:
                st.session_state["search_bg"]      = blood_group
                st.session_state["search_city"]    = city
                st.session_state["search_area"]    = area
                st.session_state["search_urgency"] = urgency
                st.session_state["current_page"]   = "Find Blood"
                st.rerun()

    st.markdown("<div class='bs-divider'></div>", unsafe_allow_html=True)

    # ── HOW IT WORKS — 5 TIER FLOW ─────────────────────────
    st.markdown("""
    <div class='sec-header'>⚙️ Smart 5-Tier Search Architecture</div>
    <p class='sec-sub'>Automated cascading fallback search — hospitals first, community donors last</p>
    """, unsafe_allow_html=True)

    tiers = [
        ("🏥", "T1 · Hospitals", "Nearest verified hospitals checked first across area & city", "#2980b9"),
        ("🏦", "T2 · Blood Banks", "Registered blood bank inventories queried second", "#27ae60"),
        ("🏕️", "T3 · Blood Camps", "Active & upcoming local donation camps checked third", "#e67e22"),
        ("🩸", "T4 · Donors", "Verified donor matching (KNN ranked) — WHO 90-day rule", "#c0392b"),
        ("📲", "T5 · SOS Share", "Viral WhatsApp broadcast link generated automatically", "#25D366"),
    ]
    cols = st.columns(5)
    for col, (icon, name, desc, color) in zip(cols, tiers):
        col.markdown(f"""
        <div class='tier-card'>
          <div style='font-size:32px;margin-bottom:12px'>{icon}</div>
          <div style='font-size:12px;font-weight:700;color:{color};
                      margin-bottom:6px;letter-spacing:0.5px'>{name}</div>
          <div style='font-size:11px;color:rgba(255,255,255,0.5);
                      line-height:1.5'>{desc}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div class='bs-divider'></div>", unsafe_allow_html=True)

    # ── DAATA WALL PREVIEW ──────────────────────────────────
    st.markdown("""
    <div class='sec-header'>🏆 Daata Wall of Honor</div>
    <p class='sec-sub'>Celebrating the real heroes saving lives across Gujarat 🩸</p>
    """, unsafe_allow_html=True)

    donors = get_all_donors_daata_wall()
    if donors:
        top3 = donors[:3]
        medals = ["🥇", "🥈", "🥉"]
        cols = st.columns(3)
        for i, (col, d) in enumerate(zip(cols, top3)):
            lives = d["donations_count"] * 3
            card_class = "podium-gold" if i == 0 else "bs-card"
            col.markdown(f"""
            <div class='{card_class}' style='text-align:center'>
              <div style='font-size:28px'>{medals[i]}</div>
              <div style='font-size:36px;margin:6px 0'>🩸</div>
              <div style='font-family:"Playfair Display",serif;font-size:17px;
                          font-weight:700;color:white'>{d["name"]}</div>
              <div style='font-size:12px;color:#e74c3c;font-weight:600;
                          margin:4px 0'>{d["blood_group"]} &nbsp;·&nbsp; {d["city"]}</div>
              <div class='stat-number'>{d["donations_count"]}</div>
              <div style='font-size:11px;color:rgba(255,255,255,0.5)'>
                donations · <span style='color:#2ecc71;font-weight:600'>❤️ {lives} lives saved</span></div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No donors on the Daata Wall yet. Register today to be the first hero! 🩸")

    st.markdown("<div class='bs-divider'></div>", unsafe_allow_html=True)

    # ── MINI ANALYTICS ─────────────────────────────────────
    st.markdown("""
    <div class='sec-header'>📊 Live Blood Availability & AI Forecast</div>
    <p class='sec-sub'>Real-time inventory and Random Forest ML shortage predictions</p>
    """, unsafe_allow_html=True)

    shortage = predict_shortage()
    groups   = list(shortage.keys())
    statuses = [shortage[g]["status"] for g in groups]
    probs    = [shortage[g]["probability"] for g in groups]

    colors = []
    for s in statuses:
        if "Critical" in s:
            colors.append("#e74c3c")
        elif "Low" in s:
            colors.append("#f0c040")
        else:
            colors.append("#2ecc71")

    fig = go.Figure(go.Bar(
        x=groups, y=probs,
        marker_color=colors,
        text=[s.split()[1] for s in statuses],
        textposition="outside",
        hovertemplate="<b>%{x}</b><br>Shortage risk: %{y}%<extra></extra>"
    ))
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="rgba(255,255,255,0.7)", family="Inter"),
        yaxis=dict(title="Shortage Risk %", gridcolor="rgba(255,255,255,0.05)", range=[0, 110]),
        xaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
        margin=dict(t=20, b=10, l=0, r=0),
        height=260,
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)

    # ── FOOTER ─────────────────────────────────────────────
    st.markdown("""
    <div class='bs-footer'>
      🩸 <b>BloodSetu Portal</b> · Parul University · BCA (Hons) Mini Project-II<br>
      Made with <span>❤️</span> to connect blood donors and save lives across Gujarat · 
      📧 bloodsetu.help@gmail.com
    </div>
    """, unsafe_allow_html=True)