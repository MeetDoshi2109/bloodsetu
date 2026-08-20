"""
pages/find_blood.py — BloodSetu 5-Tier Search Page
Complete cascading search T1 → T5
"""

import streamlit as st
import time
from database import post_sos
from ml_model import tier_search
from utils import (GUJARAT_CITIES, get_areas, ALL_BLOOD_GROUPS,
                   wa_sos_message, get_compatible_groups, get_msg)
from map_handler import build_map, show_map


def show():
    st.markdown("""
    <div class='sec-header'>🔍 Find Blood</div>
    <p class='sec-sub'>No login needed. Search instantly across all of Gujarat.</p>
    """, unsafe_allow_html=True)

    # ── SEARCH FORM ────────────────────────────────────────
    with st.form("find_blood_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            blood_group = st.selectbox(
                "🩸 Blood Group",
                ALL_BLOOD_GROUPS,
                index=ALL_BLOOD_GROUPS.index(
                    st.session_state.get("search_bg", "B+")
                ) if st.session_state.get("search_bg") in ALL_BLOOD_GROUPS else 0
            )
        with col2:
            city = st.selectbox(
                "📍 City",
                GUJARAT_CITIES,
                index=GUJARAT_CITIES.index(
                    st.session_state.get("search_city", "Vadodara")
                ) if st.session_state.get("search_city") in GUJARAT_CITIES else 0
            )
        with col3:
            areas = get_areas(city)
            area = st.selectbox("📍 Area in City", areas if areas else ["—"])

        # Double confirm location
        confirm = st.checkbox(
            f"✅ Confirm: I need blood in **{area}, {city}**",
            value=True
        )
        urgency = st.radio(
            "⚡ Urgency Level",
            ["🔴 Critical", "🟡 Urgent", "🟢 Planned"],
            horizontal=True
        )
        search_btn = st.form_submit_button(
            "🔍 Find Blood Now",
            use_container_width=True
        )

    if not search_btn:
        _show_compatible_hint(blood_group)
        return

    if not confirm:
        st.warning("Please confirm your location before searching.")
        return

    # ── ANIMATED LOADER ────────────────────────────────────
    st.markdown(f"""
    <div class='msg-box'>
      <b>{get_msg("search_loading","en")}</b><br>
      <span style='color:rgba(255,255,255,0.4)'>{get_msg("search_loading","gu")}</span>
    </div>
    """, unsafe_allow_html=True)

    progress = st.progress(0)
    status_txt = st.empty()

    steps = [
        (25,  "🏥 Checking hospitals in your area..."),
        (50,  "🏦 Checking blood banks..."),
        (75,  "🏕️ Searching blood camps..."),
        (100, "🩸 Looking for eligible donors..."),
    ]
    for pct, msg in steps:
        status_txt.markdown(f"<p style='color:#e74c3c;font-size:13px'>{msg}</p>",
                            unsafe_allow_html=True)
        progress.progress(pct)
        time.sleep(0.4)

    status_txt.empty()
    progress.empty()

    # ── TIER SEARCH ────────────────────────────────────────
    results = tier_search(blood_group, city, area)
    found_at = results["found_at"]

    # ── SEEKER DETAILS FORM ────────────────────────────────
    st.markdown("---")
    st.markdown("""
    <div style='background:rgba(192,57,43,0.08);border:1px solid rgba(192,57,43,0.25);
    border-radius:12px;padding:16px 20px;margin-bottom:16px'>
      <h4 style='color:#f0c040;font-family:Playfair Display,serif;margin:0 0 6px'>
        📋 Share Your Details to See Contact Info
      </h4>
      <p style='font-size:12px;color:rgba(255,255,255,0.5);margin:0'>
        Required before any contact is revealed. Your details will be shared with the provider so they can reach you too.
      </p>
    </div>
    """, unsafe_allow_html=True)

    with st.form("seeker_details_form"):
        sc1, sc2, sc3 = st.columns(3)
        with sc1:
            s_name  = st.text_input("Your Name *")
        with sc2:
            s_phone = st.text_input("Your Phone Number *")
        with sc3:
            s_area  = st.text_input("Your Current Area *", value=area)
        reveal = st.form_submit_button(
            "✅ Show Me the Contact",
            use_container_width=True
        )

    if not reveal:
        return

    if not s_name or not s_phone or not s_area:
        st.warning("Please fill all three fields — name, phone and area.")
        return

    # ── SHOW RESULTS ───────────────────────────────────────
    _show_results(results, found_at, blood_group, city, area,
                  s_name, s_phone, s_area, urgency)

    # Save SOS to DB
    post_sos(blood_group, city, area, s_name, s_phone,
             urgency.split()[1] if " " in urgency else urgency)


def _show_compatible_hint(blood_group: str):
    compatible = get_compatible_groups(blood_group)
    if len(compatible) > 1:
        st.info(
            f"💡 **Auto-compatibility:** When searching for {blood_group}, "
            f"we also check: {', '.join(compatible)} donors/hospitals — "
            "more results = more chances to find help!"
        )


def _show_results(results, found_at, blood_group, city, area,
                  s_name, s_phone, s_area, urgency):

    # T1 — Hospitals
    if results["T1_hospitals"]:
        st.markdown("""
        <div class='msg-box-success'>
          ✅ <b>Hope found. Someone is ready to help you.</b><br>
          <span style='color:rgba(255,255,255,0.5)'>
          આશા મળી. કોઈ તમારી મદદ કરવા તૈયાર છે. ❤️</span>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div style='background:rgba(41,128,185,0.1);border-left:4px solid #2980b9;
        border-radius:8px;padding:8px 14px;margin-bottom:12px'>
          <span style='color:#5dade2;font-weight:700;font-size:12px'>
          🏥 T1 · HOSPITALS FOUND</span>
        </div>
        """, unsafe_allow_html=True)
        for h in results["T1_hospitals"]:
            _hospital_card(h, s_name, s_phone, s_area)

    # T2 — Blood Banks
    if results["T2_banks"]:
        st.markdown("""
        <div style='background:rgba(46,204,113,0.1);border-left:4px solid #27ae60;
        border-radius:8px;padding:8px 14px;margin-bottom:12px'>
          <span style='color:#2ecc71;font-weight:700;font-size:12px'>
          🏦 T2 · BLOOD BANKS FOUND</span>
        </div>
        """, unsafe_allow_html=True)
        for b in results["T2_banks"]:
            _bank_card(b, s_name, s_phone, s_area)

    # T3 — Camps
    if results["T3_camps"]:
        st.markdown("""
        <div style='background:rgba(230,126,34,0.1);border-left:4px solid #e67e22;
        border-radius:8px;padding:8px 14px;margin-bottom:12px'>
          <span style='color:#e67e22;font-weight:700;font-size:12px'>
          🏕️ T3 · BLOOD CAMPS FOUND</span>
        </div>
        """, unsafe_allow_html=True)
        for c in results["T3_camps"]:
            _camp_card(c, s_name, s_phone, s_area)

    # T4 — Donors
    if results["T4_donors"]:
        st.markdown("""
        <div style='background:rgba(192,57,43,0.1);border-left:4px solid #c0392b;
        border-radius:8px;padding:8px 14px;margin-bottom:12px'>
          <span style='color:#e74c3c;font-weight:700;font-size:12px'>
          🩸 T4 · DONORS FOUND (Emergency)</span>
        </div>
        """, unsafe_allow_html=True)
        st.warning(
            "⏱️ **2-Hour Privacy Window:** Donor contact is visible for 2 hours only. "
            "Please reach out immediately."
        )
        # One donor per request — show top match first
        shown = set()
        for d in results["T4_donors"]:
            if d["id"] not in shown:
                shown.add(d["id"])
                _donor_card(d, s_name, s_phone, s_area)

    # T5 — WhatsApp SOS
    if found_at == "T5":
        st.markdown("""
        <div class='msg-box'>
          <b>We searched everywhere. Don't give up yet.</b><br>
          <span style='color:rgba(255,255,255,0.4)'>
          અમે બધે શોધ્યું. હજી હાર ન માનો. ❤️</span>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div style='background:rgba(37,211,102,0.06);
        border:1px solid rgba(37,211,102,0.25);border-radius:12px;
        padding:16px;margin:12px 0'>
          <p style='color:#25D366;font-weight:700;margin:0 0 10px'>
          📲 Share this SOS on WhatsApp:</p>
        </div>
        """, unsafe_allow_html=True)
        msg = wa_sos_message(blood_group, area, city, s_phone)
        st.code(msg, language=None)
        st.info(
            "📋 Copy this message and share in your WhatsApp groups. "
            "Sometimes miracles come from unexpected places. ❤️"
        )

    # MAP
    if found_at != "T5":
        st.markdown("---")
        st.markdown("**🗺️ Location Map**")
        m = build_map(
            area, city,
            hospitals=results["T1_hospitals"] or None,
            banks=results["T2_banks"] or None,
            camps=results["T3_camps"] or None,
            donors=results["T4_donors"] or None,
        )
        show_map(m, height=350)


def _hospital_card(h, s_name, s_phone, s_area):
    st.markdown(f"""
    <div class='result-card'>
      <h4>🏥 {h["name"]} {'✅' if h["is_verified"] else ''}</h4>
      <p>👨‍⚕️ {h.get("doctor_name","—")} &nbsp;|&nbsp;
         📍 {h["area"]}, {h["city"]}</p>
      <p>🩸 Blood Available: <b style='color:#e74c3c'>{h.get("blood_available","—")}</b></p>
      <p>⏰ Emergency 24×7: {"✅ Yes" if h["emergency_24x7"] else "❌ No"}</p>
      <p style='color:#f0c040'>📞 <b>{h["phone"]}</b></p>
      <p style='font-size:11px;color:rgba(255,255,255,0.35)'>
      Seeker details shared with hospital: {s_name} · {s_phone} · {s_area}</p>
    </div>
    """, unsafe_allow_html=True)
    _wa_share_btn(h["phone"], h["name"])


def _bank_card(b, s_name, s_phone, s_area):
    st.markdown(f"""
    <div class='result-card'>
      <h4>🏦 {b["name"]} {'✅' if b["is_verified"] else ''}</h4>
      <p>👨‍⚕️ {b.get("doctor_name","—")} &nbsp;|&nbsp;
         📍 {b["area"]}, {b["city"]}</p>
      <p>🩸 Groups Available: <b style='color:#e74c3c'>
         {b.get("groups_available","—")}</b></p>
      <p style='color:#f0c040'>📞 <b>{b["phone"]}</b></p>
      <p style='font-size:11px;color:rgba(255,255,255,0.35)'>
      Seeker details shared: {s_name} · {s_phone} · {s_area}</p>
    </div>
    """, unsafe_allow_html=True)
    _wa_share_btn(b["phone"], b["name"])


def _camp_card(c, s_name, s_phone, s_area):
    st.markdown(f"""
    <div class='result-card'>
      <h4>🏕️ {c["organizer"]} {'✅' if c["is_verified"] else ''}</h4>
      <p>👨‍⚕️ {c.get("doctor_name","—")} &nbsp;|&nbsp;
         📍 {c["area"]}, {c["city"]}</p>
      <p>📅 Date: <b>{c["camp_date"]}</b> &nbsp;|&nbsp;
         ⏰ {c.get("timings","—")}</p>
      <p style='color:#f0c040'>📞 <b>{c["phone"]}</b></p>
      <p style='font-size:11px;color:rgba(255,255,255,0.35)'>
      Seeker details shared: {s_name} · {s_phone} · {s_area}</p>
    </div>
    """, unsafe_allow_html=True)
    _wa_share_btn(c["phone"], c["organizer"])


def _donor_card(d, s_name, s_phone, s_area):
    st.markdown(f"""
    <div class='result-card' style='border-left-color:#e74c3c'>
      <h4>🩸 {d["name"]}</h4>
      <p>💉 Blood Group: <b style='color:#e74c3c'>{d["blood_group"]}</b>
         &nbsp;|&nbsp; 📍 {d["area"]}, {d["city"]}</p>
      <p style='color:#f0c040'>📞 <b>{d["phone"]}</b>
         <span style='font-size:11px;color:#ff6b6b'>
         &nbsp; ⏱️ Visible for 2 hours only</span></p>
      <p style='font-size:11px;color:rgba(255,255,255,0.35)'>
      Seeker details shared: {s_name} · {s_phone} · {s_area}</p>
    </div>
    """, unsafe_allow_html=True)


def _wa_share_btn(phone: str, name: str):
    with st.expander("📤 Generate WhatsApp Message"):
        msg = (
            f"🩸 *BloodSetu* — Blood required urgently.\n"
            f"Please contact: *{name}*\n"
            f"📞 {phone}\n\n"
            "BloodSetu — Connecting Hearts, Saving Lives 🩸"
        )
        st.code(msg, language=None)
        st.caption("Copy this message and share on WhatsApp")
        