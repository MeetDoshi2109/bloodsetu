"""
pages/daata_wall.py — BloodSetu Daata Wall of Honor
Top donors, lives saved, badges showcase
"""

import streamlit as st
from database import get_all_donors_daata_wall, get_platform_stats
from utils import get_earned_badges, wa_awareness_message


def show():
    st.markdown("""
    <div style='text-align:center;padding:20px 0 10px'>
      <p style='font-size:36px;margin:0'>🏆</p>
      <h1 style='font-family:Playfair Display,serif;font-size:32px;
                 color:white;margin:8px 0 4px'>Daata Wall of Honor</h1>
      <p style='color:rgba(255,255,255,0.5);font-style:italic;font-size:15px'>
        These are not just names. These are people who said YES<br>
        when someone needed them most. These are real heroes. 🩸</p>
      <p style='color:rgba(255,255,255,0.3);font-size:13px'>
        આ ફક્ત નામ નથી. આ સાચા હીરો છે.</p>
    </div>
    """, unsafe_allow_html=True)

    stats = get_platform_stats()
    c1, c2, c3 = st.columns(3)
    c1.metric("🩸 Registered Donors", stats["donors"])
    c2.metric("❤️ Total Donations", stats["donations"])
    c3.metric("💉 Lives Potentially Saved", stats["donations"] * 3)

    st.markdown("---")

    donors = get_all_donors_daata_wall()

    if not donors:
        st.info(
            "The Daata Wall is empty for now. "
            "Be the first hero to register and opt in! 🩸"
        )
        return

    # ── PODIUM TOP 3 ────────────────────────────────────────
    if len(donors) >= 1:
        st.markdown("### 🥇 Champions of Hope")
        top3 = donors[:3]
        medals = ["🥇", "🥈", "🥉"]
        gold_styles = [
            "border:1px solid #f0c040;box-shadow:0 0 24px rgba(240,192,64,0.25)",
            "border:1px solid rgba(192,57,43,0.35)",
            "border:1px solid rgba(192,57,43,0.35)",
        ]
        cols = st.columns(len(top3))
        for i, (col, d) in enumerate(zip(cols, top3)):
            badges = get_earned_badges(d["donations_count"], d["blood_group"])
            badge_icons = " ".join(b["icon"] for b in badges)
            lives = d["donations_count"] * 3
            col.markdown(f"""
            <div style='background:rgba(255,255,255,0.04);{gold_styles[i]};
            border-radius:18px;padding:24px 16px;text-align:center'>
              <div style='font-size:30px'>{medals[i]}</div>
              <div style='font-size:40px;margin:8px 0'>🩸</div>
              <div style='font-family:Playfair Display,serif;font-size:17px;
                          font-weight:700;color:white'>{d["name"]}</div>
              <div style='font-size:13px;color:#e74c3c;font-weight:600;margin:4px 0'>
                {d["blood_group"]}</div>
              <div style='font-size:28px;font-weight:700;color:#f0c040;line-height:1'>
                {d["donations_count"]}</div>
              <div style='font-size:10px;color:rgba(255,255,255,0.4)'>
                donations</div>
              <div style='font-size:13px;color:#2ecc71;margin:6px 0'>
                ❤️ {lives} lives potentially saved</div>
              <div style='font-size:18px;margin-top:8px'>{badge_icons}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # ── FULL LEADERBOARD ────────────────────────────────────
    st.markdown("### 📋 Full Leaderboard")
    for rank, d in enumerate(donors, 1):
        badges = get_earned_badges(d["donations_count"], d["blood_group"])
        badge_icons = " ".join(b["icon"] for b in badges)
        lives = d["donations_count"] * 3

        rank_icon = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else f"#{rank}"

        st.markdown(f"""
        <div class='bs-card' style='display:flex;align-items:center;gap:16px'>
          <div style='font-size:20px;min-width:36px;text-align:center'>{rank_icon}</div>
          <div style='font-size:32px'>🩸</div>
          <div style='flex:1'>
            <div style='font-weight:700;color:white;font-size:15px'>{d["name"]}</div>
            <div style='font-size:12px;color:#e74c3c;font-weight:600'>
              {d["blood_group"]} &nbsp;|&nbsp;
              <span style='color:rgba(255,255,255,0.5)'>
              📍 {d["area"]}, {d["city"]}</span></div>
            <div style='font-size:11px;margin-top:4px'>{badge_icons}</div>
          </div>
          <div style='text-align:right'>
            <div style='font-family:Playfair Display,serif;font-size:24px;
                        color:#f0c040;font-weight:700'>{d["donations_count"]}</div>
            <div style='font-size:10px;color:rgba(255,255,255,0.4)'>donations</div>
            <div style='font-size:11px;color:#2ecc71'>❤️ {lives} lives</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # ── AWARENESS SHARE ─────────────────────────────────────
    st.markdown("### 📤 Spread the Word")
    st.markdown("""
    <div class='msg-box'>
      <b>Inspired by these heroes? Share BloodSetu with your family and friends!</b><br>
      <span style='color:rgba(255,255,255,0.4)'>
      આ હીરોથી પ્રેરિત? BloodSetu ને તમારા પરિવાર સાથે શેર કરો!</span>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("📲 Generate WhatsApp Awareness Message"):
        st.code(wa_awareness_message(), language=None)
        st.caption("Copy and share in your WhatsApp groups 🩸")

    st.markdown("""
    <div class='bs-footer'>
      🏆 BloodSetu Daata Wall · Celebrating Gujarat's Blood Heroes<br>
      To appear here, register as a donor and opt into the Daata Wall ❤️
    </div>
    """, unsafe_allow_html=True)
    