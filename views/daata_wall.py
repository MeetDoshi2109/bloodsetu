"""
pages/daata_wall.py — BloodSetu Daata Wall of Honor
Top donors, lives saved, badges showcase
"""

import streamlit as st
from database import get_all_donors_daata_wall, get_platform_stats
from utils import get_earned_badges, wa_awareness_message


def show():
    st.markdown("""
    <div style='text-align:center;padding:24px 0 14px'>
      <p style='font-size:42px;margin:0'>🏆</p>
      <h1 style='font-family:"Playfair Display",serif;font-size:36px;
                 color:white;margin:8px 0 4px'>Daata Wall of Honor</h1>
      <p style='color:rgba(255,255,255,0.6);font-style:italic;font-size:15px'>
        Recognizing the community heroes who stepped forward to save lives across Gujarat. 🩸</p>
      <p style='color:rgba(255,255,255,0.35);font-size:13px;margin-top:2px'>
        આ ફક્ત નામ નથી. આ સાચા હીરો છે.</p>
    </div>
    """, unsafe_allow_html=True)

    stats = get_platform_stats()
    c1, c2, c3 = st.columns(3)
    c1.metric("🩸 Registered Donors", stats["donors"])
    c2.metric("❤️ Total Donations", stats["donations"])
    c3.metric("💉 Lives Potentially Saved", stats["donations"] * 3)

    st.markdown("<div class='bs-divider'></div>", unsafe_allow_html=True)

    donors = get_all_donors_daata_wall()

    if not donors:
        st.info(
            "The Daata Wall is empty. "
            "Be the first hero to register as a donor and opt into the Hall of Honor! 🩸"
        )
        return

    # ── PODIUM TOP 3 ────────────────────────────────────────
    if len(donors) >= 1:
        st.markdown("### 🥇 Top Champions of Hope")
        top3 = donors[:3]
        medals = ["🥇", "🥈", "🥉"]
        cols = st.columns(len(top3))
        for i, (col, d) in enumerate(zip(cols, top3)):
            badges = get_earned_badges(d["donations_count"], d["blood_group"])
            badge_icons = " ".join(b["icon"] for b in badges)
            lives = d["donations_count"] * 3
            card_class = "podium-gold" if i == 0 else "bs-card"

            col.markdown(f"""
            <div class='{card_class}' style='text-align:center'>
              <div style='font-size:32px'>{medals[i]}</div>
              <div style='font-size:40px;margin:8px 0'>🩸</div>
              <div style='font-family:"Playfair Display",serif;font-size:18px;
                          font-weight:700;color:white'>{d["name"]}</div>
              <div style='font-size:13px;color:#e74c3c;font-weight:600;margin:4px 0'>
                {d["blood_group"]} &nbsp;·&nbsp; {d["city"]}</div>
              <div class='stat-number'>{d["donations_count"]}</div>
              <div style='font-size:11px;color:rgba(255,255,255,0.5)'>donations</div>
              <div style='font-size:13px;color:#2ecc71;font-weight:600;margin:6px 0'>
                ❤️ {lives} lives saved</div>
              <div style='font-size:20px;margin-top:8px'>{badge_icons}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div class='bs-divider'></div>", unsafe_allow_html=True)

    # ── FULL LEADERBOARD ────────────────────────────────────
    st.markdown("### 📋 Full Leaderboard")
    for rank, d in enumerate(donors, 1):
        badges = get_earned_badges(d["donations_count"], d["blood_group"])
        badge_icons = " ".join(b["icon"] for b in badges)
        lives = d["donations_count"] * 3
        rank_icon = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else f"#{rank}"

        st.markdown(f"""
        <div class='bs-card' style='display:flex;align-items:center;gap:18px;padding:16px 20px'>
          <div style='font-size:22px;min-width:40px;text-align:center;font-weight:700;color:#f0c040'>{rank_icon}</div>
          <div style='font-size:32px'>🩸</div>
          <div style='flex:1'>
            <div style='font-weight:700;color:white;font-size:16px'>{d["name"]}</div>
            <div style='font-size:12px;color:#e74c3c;font-weight:600;margin-top:2px'>
              {d["blood_group"]} &nbsp;|&nbsp;
              <span style='color:rgba(255,255,255,0.55);font-weight:400'>
              📍 {d["area"]}, {d["city"]}</span></div>
            <div style='font-size:12px;margin-top:4px'>{badge_icons}</div>
          </div>
          <div style='text-align:right'>
            <div style='font-family:"Playfair Display",serif;font-size:26px;
                        color:#f0c040;font-weight:700'>{d["donations_count"]}</div>
            <div style='font-size:10px;color:rgba(255,255,255,0.45)'>donations</div>
            <div style='font-size:11px;color:#2ecc71;font-weight:600'>❤️ {lives} lives</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div class='bs-divider'></div>", unsafe_allow_html=True)

    # ── AWARENESS SHARE ─────────────────────────────────────
    st.markdown("### 📤 Inspire Others")
    st.markdown("""
    <div class='msg-box'>
      <b>Spread the word and invite friends to join Gujarat's blood network!</b><br>
      <span style='color:rgba(255,255,255,0.45)'>આ હીરોથી પ્રેરિત? BloodSetu ને તમારા પરિવાર સાથે શેર કરો!</span>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("📲 Generate WhatsApp Awareness Broadcast"):
        st.code(wa_awareness_message(), language=None)
        st.caption("Copy and share in your WhatsApp groups 🩸")

    st.markdown("""
    <div class='bs-footer'>
      🏆 BloodSetu Daata Wall of Honor · Celebrating Gujarat's Blood Heroes<br>
      To appear here, register as a donor and opt into public wall display. ❤️
    </div>
    """, unsafe_allow_html=True)