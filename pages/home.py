"""
pages/home.py — BloodSetu Homepage
Split screen hero, search, stats, tier flow, Daata Wall preview, analytics strip
"""

import streamlit as st
import plotly.graph_objects as go
from database import (get_platform_stats, get_all_donors_daata_wall,
                      get_active_sos, expire_old_sos)
from utils import (GUJARAT_CITIES, get_areas, get_compatible_groups,
                   ALL_BLOOD_GROUPS, QUOTES, get_msg)
from ml_model import predict_shortage
import random


def show():
    # expire old SOS first
    expire_old_sos()

    # ── URGENCY BANNER ──────────────────────────────────────
    active_sos = get_active_sos()
    if active_sos:
        sos = active_sos[0]
        st.markdown(f"""
        <div style='background:linear-gradient(90deg,#7b0d0d,#c0392b,#7b0d0d);
        padding:10px 20px;border-radius:8px;margin-bottom:16px;
        display:flex;align-items:center;gap:12px'>
        <span style='color:#ff4444;font-size:18px;animation:blink 0.8s infinite'>🔴</span>
        <span style='color:white;font-size:13px;font-weight:600'>
        🚨 URGENT: <b>{sos["blood_group"]}</b> blood needed in
        <b>{sos["area"]}, {sos["city"]}</b> —
        Contact: {sos["seeker_phone"]} · Posted {sos["posted_at"][:16]}
        </span></div>
        """, unsafe_allow_html=True)

    # ── HERO SPLIT SCREEN ───────────────────────────────────
    left, right = st.columns([1, 1], gap="large")

    with left:
        # Mascot SVG
        st.markdown("""
        <div style='text-align:center;margin-bottom:16px'>
        <svg width='90' height='108' viewBox='0 0 80 96' fill='none'
             style='animation:float 3s ease-in-out infinite;
             filter:drop-shadow(0 0 20px rgba(231,76,60,0.7))'>
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
              <stop offset='0%' stop-color='#e74c3c'/>
              <stop offset='100%' stop-color='#7b241c'/>
            </linearGradient>
          </defs>
        </svg></div>
        <style>
        @keyframes float{0%,100%{transform:translateY(0) rotate(-2deg)}
                         50%{transform:translateY(-10px) rotate(2deg)}}
        </style>
        """, unsafe_allow_html=True)

        # Quote (random, bilingual)
        q = random.choice(QUOTES)
        st.markdown(f"""
        <div style='border-left:3px solid #c0392b;padding-left:14px;margin-bottom:18px'>
          <p style='font-family:Playfair Display,serif;font-size:22px;
                    font-weight:700;color:white;margin:0;line-height:1.3'>
            {q["en"]}
          </p>
          <p style='font-size:14px;color:rgba(255,255,255,0.55);
                    margin:6px 0 0;font-style:italic'>
            {q["gu"]}
          </p>
        </div>
        """, unsafe_allow_html=True)

        # Live stats
        stats = get_platform_stats()
        c1, c2, c3 = st.columns(3)
        c1.metric("🩸 Donors", stats["donors"])
        c2.metric("🏥 Hospitals", stats["hospitals"])
        c3.metric("❤️ Donations", stats["donations"])

        st.markdown("<br>", unsafe_allow_html=True)

        # SOS button
        st.markdown("""
        <a href='#' style='display:block;width:100%;padding:14px;
        background:linear-gradient(135deg,#7b0d0d,#c0392b);
        color:white;border-radius:12px;text-align:center;
        font-weight:700;font-size:15px;letter-spacing:1px;
        text-decoration:none;box-shadow:0 0 20px rgba(192,57,43,0.5)'>
        🚨 EMERGENCY SOS
        </a>
        """, unsafe_allow_html=True)

    with right:
        st.markdown("""
        <div style='background:rgba(255,255,255,0.04);border:1px solid rgba(192,57,43,0.25);
        border-radius:18px;padding:28px 24px;
        box-shadow:0 0 40px rgba(192,57,43,0.1)'>
        <h2 style='font-family:Playfair Display,serif;font-size:22px;
                   color:white;margin-bottom:6px'>🔍 Find Blood Now</h2>
        <p style='font-size:12px;color:rgba(255,255,255,0.5);
                  margin-bottom:18px'>No login needed. Just tell us what you need.</p>
        </div>
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
            # Double confirm location
            confirm_loc = st.checkbox(
                f"✅ Confirm: I need blood in **{area}, {city}**",
                key="home_confirm"
            )
            urgency = st.radio(
                "⚡ Urgency",
                ["🔴 Critical", "🟡 Urgent", "🟢 Planned"],
                horizontal=True,
                key="home_urgency"
            )

            submitted = st.form_submit_button(
                "🔍 Find Blood Now",
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
                st.session_state["go_to_search"]   = True
                st.switch_page("pages/find_blood.py")

    st.markdown("---")

    # ── HOW IT WORKS — 5 TIER FLOW ─────────────────────────
    st.markdown("""
    <div class='sec-header'>⚙️ How BloodSetu Works</div>
    <p class='sec-sub'>We search everywhere automatically — hospitals first, donors last</p>
    """, unsafe_allow_html=True)

    tiers = [
        ("🏥", "T1 · Hospitals", "Nearest verified hospitals — area → city → Gujarat", "#2980b9"),
        ("🏦", "T2 · Blood Banks", "Registered blood banks searched next", "#27ae60"),
        ("🏕️", "T3 · Blood Camps", "Active & upcoming camps checked third", "#e67e22"),
        ("🩸", "T4 · Donors", "Emergency last resort — WHO 90-day rule enforced", "#c0392b"),
        ("📲", "T5 · SOS Share", "WhatsApp shareable message — spreads virally", "#25D366"),
    ]
    cols = st.columns(5)
    for col, (icon, name, desc, color) in zip(cols, tiers):
        col.markdown(f"""
        <div style='background:rgba(255,255,255,0.04);border:1px solid rgba(192,57,43,0.2);
        border-radius:14px;padding:18px 12px;text-align:center;height:180px'>
          <div style='font-size:28px;margin-bottom:10px'>{icon}</div>
          <div style='font-size:12px;font-weight:700;color:{color};
                      margin-bottom:6px'>{name}</div>
          <div style='font-size:10px;color:rgba(255,255,255,0.5);
                      line-height:1.5'>{desc}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # ── DAATA WALL PREVIEW ──────────────────────────────────
    st.markdown("""
    <div class='sec-header'>🏆 Daata Wall — Hall of Heroes</div>
    <p class='sec-sub'>These are not just names. These are real heroes. 🩸</p>
    """, unsafe_allow_html=True)

    donors = get_all_donors_daata_wall()
    if donors:
        # Podium top 3
        top3 = donors[:3]
        medals = ["🥇", "🥈", "🥉"]
        cols = st.columns(3)
        for i, (col, d) in enumerate(zip(cols, top3)):
            lives = d["donations_count"] * 3
            col.markdown(f"""
            <div style='background:rgba(255,255,255,0.04);
            border:1px solid {"#f0c040" if i==0 else "rgba(192,57,43,0.25)"};
            border-radius:16px;padding:20px;text-align:center;
            box-shadow:{"0 0 20px rgba(240,192,64,0.2)" if i==0 else "none"}'>
              <div style='font-size:28px'>{medals[i]}</div>
              <div style='font-size:36px;margin:8px 0'>🩸</div>
              <div style='font-family:Playfair Display,serif;font-size:16px;
                          font-weight:700;color:white'>{d["name"]}</div>
              <div style='font-size:12px;color:#e74c3c;font-weight:600;
                          margin:4px 0'>{d["blood_group"]}</div>
              <div style='font-size:24px;font-weight:700;
                          color:#f0c040'>{d["donations_count"]}</div>
              <div style='font-size:10px;color:rgba(255,255,255,0.5)'>
                donations · {lives} lives potentially saved</div>
            </div>
            """, unsafe_allow_html=True)

        # Remaining grid
        if len(donors) > 3:
            st.markdown("<br>", unsafe_allow_html=True)
            rest = donors[3:]
            cols2 = st.columns(min(len(rest), 4))
            for col, d in zip(cols2, rest):
                col.markdown(f"""
                <div style='background:rgba(255,255,255,0.03);
                border:1px solid rgba(192,57,43,0.18);border-radius:12px;
                padding:14px;text-align:center'>
                  <div style='font-size:22px'>🩸</div>
                  <div style='font-size:13px;font-weight:600;
                              color:white;margin:6px 0'>{d["name"]}</div>
                  <div style='font-size:11px;color:#e74c3c'>{d["blood_group"]}</div>
                  <div style='font-size:11px;color:rgba(255,255,255,0.4)'>
                    {d["donations_count"]} donations</div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No donors on the Daata Wall yet. Be the first hero! 🩸")

    st.markdown("---")

    # ── MINI ANALYTICS ─────────────────────────────────────
    st.markdown("""
    <div class='sec-header'>📊 Blood Availability — Gujarat</div>
    <p class='sec-sub'>Live status across all registered hospitals and blood banks</p>
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
        font=dict(color="rgba(255,255,255,0.7)", family="Poppins"),
        yaxis=dict(title="Shortage Risk %", gridcolor="rgba(255,255,255,0.05)"),
        xaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
        margin=dict(t=20, b=10, l=0, r=0),
        height=260,
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("""
    <p style='text-align:center;font-size:12px;color:rgba(255,255,255,0.35)'>
    Click any bar for full analytics dashboard</p>
    """, unsafe_allow_html=True)

    # ── EMOTIONAL FOOTER QUOTE ──────────────────────────────
    st.markdown("""
    <div style='background:linear-gradient(135deg,#200808,#1a0505);
    border:1px solid rgba(192,57,43,0.2);border-radius:14px;
    padding:28px;text-align:center;margin-top:20px'>
      <p style='font-family:Playfair Display,serif;font-size:20px;
                font-style:italic;color:white;margin:0 0 8px'>
        "You don't need a cape to be a hero.<br>
        You just need to say <span style='color:#e74c3c'>YES</span>."
      </p>
      <p style='font-size:13px;color:rgba(255,255,255,0.4);margin:0'>
        હીરો બનવા માટે ઝભ્ભો નથી જોઈતો. ફક્ત 'હા' કહો.
      </p>
    </div>
    """, unsafe_allow_html=True)

    # ── FOOTER ─────────────────────────────────────────────
    st.markdown("""
    <div class='bs-footer'>
      🩸 BloodSetu · Parul University · BCA (Hons) Mini Project-II<br>
      Made with <span>❤️</span> to save lives across Gujarat ·
      📧 bloodsetu.help@gmail.com
    </div>
    """, unsafe_allow_html=True)
    