"""
pages/admin.py — BloodSetu Admin Panel
Verify hospitals, banks, camps. Review fraud reports. Platform stats.
"""

import streamlit as st
from auth import require_login, current_role
from database import (get_pending_hospitals, get_pending_banks, get_pending_camps,
                      verify_hospital, verify_blood_bank, verify_camp,
                      get_platform_stats, get_all_hospitals, get_all_blood_banks,
                      get_all_camps, get_all_donors_daata_wall)
from fraud import admin_fraud_panel


def show():
    st.markdown("""
    <div class='sec-header'>👑 Admin Panel</div>
    <p class='sec-sub'>BloodSetu system administration — owner access only</p>
    """, unsafe_allow_html=True)

    if not require_login("admin"):
        return

    if current_role() != "admin":
        st.error("❌ Admin access only.")
        return

    stats = get_platform_stats()

    # ── STATS ─────────────────────────────────────────────
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("🩸 Donors", stats["donors"])
    c2.metric("🏥 Hospitals", stats["hospitals"])
    c3.metric("🏦 Blood Banks", stats["banks"])
    c4.metric("🏕️ Camps", stats["camps"])
    c5.metric("❤️ Donations", stats["donations"])

    if stats["pending_reports"] > 0:
        st.error(f"🚨 {stats['pending_reports']} pending fraud report(s) need review!")

    st.markdown("---")

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🏥 Hospitals",
        "🏦 Blood Banks",
        "🏕️ Camps",
        "🛡️ Fraud Reports",
        "📋 All Data",
    ])

    with tab1:
        _verify_tab(
            "Hospital",
            get_pending_hospitals,
            verify_hospital,
            ["name", "doctor_name", "address", "city", "area", "phone", "emergency_24x7"],
        )

    with tab2:
        _verify_tab(
            "Blood Bank",
            get_pending_banks,
            verify_blood_bank,
            ["name", "doctor_name", "city", "area", "phone"],
        )

    with tab3:
        _verify_tab(
            "Blood Camp",
            get_pending_camps,
            verify_camp,
            ["organizer", "doctor_name", "city", "area", "phone", "camp_date", "timings"],
        )

    with tab4:
        admin_fraud_panel()

    with tab5:
        _all_data_tab()


def _verify_tab(label, get_pending_fn, verify_fn, fields):
    pending = get_pending_fn()

    if not pending:
        st.success(f"✅ No pending {label} verifications.")
    else:
        st.markdown(f"**{len(pending)} pending {label}(s) waiting for verification:**")
        for item in pending:
            with st.container():
                st.markdown(f"""
                <div class='bs-card'>
                  <p style='font-weight:700;color:white;font-size:15px;margin:0 0 8px'>
                  {item.get("name") or item.get("organizer","—")}</p>
                """, unsafe_allow_html=True)

                for f in fields:
                    val = item.get(f, "—")
                    label_clean = f.replace("_", " ").title()
                    st.markdown(
                        f"<p style='font-size:12px;color:rgba(255,255,255,0.5);margin:2px 0'>"
                        f"<b>{label_clean}:</b> {val}</p>",
                        unsafe_allow_html=True
                    )
                st.markdown("</div>", unsafe_allow_html=True)

                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"✅ Verify", key=f"verify_{label}_{item['id']}"):
                        verify_fn(item["id"])
                        st.success(f"{label} verified and now live on BloodSetu!")
                        st.rerun()
                with col2:
                    if st.button(f"❌ Reject", key=f"reject_{label}_{item['id']}"):
                        # For now just a confirmation — deletion can be added
                        st.warning(
                            "Rejection noted. To delete, contact the database directly. "
                            "Future version will add auto-delete."
                        )
                st.divider()


def _all_data_tab():
    st.markdown("### 📋 All Verified Data")

    with st.expander("🏥 All Hospitals"):
        hospitals = get_all_hospitals()
        if hospitals:
            for h in hospitals:
                st.markdown(
                    f"**{h['name']}** · {h['city']} · {h['phone']} · "
                    f"Stock: {h.get('blood_available','—')}"
                )
        else:
            st.info("No hospitals yet.")

    with st.expander("🏦 All Blood Banks"):
        banks = get_all_blood_banks()
        if banks:
            for b in banks:
                st.markdown(
                    f"**{b['name']}** · {b['city']} · {b['phone']} · "
                    f"Groups: {b.get('groups_available','—')}"
                )
        else:
            st.info("No blood banks yet.")

    with st.expander("🏕️ All Camps"):
        camps = get_all_camps(active_only=False)
        if camps:
            for c in camps:
                st.markdown(
                    f"**{c['organizer']}** · {c['city']} · "
                    f"{c['camp_date']} · {c['phone']}"
                )
        else:
            st.info("No camps yet.")

    with st.expander("🩸 All Donors (Daata Wall)"):
        donors = get_all_donors_daata_wall()
        if donors:
            for d in donors:
                st.markdown(
                    f"**{d['name']}** · {d['blood_group']} · "
                    f"{d['city']} · {d['donations_count']} donations"
                )
        else:
            st.info("No donors on Daata Wall yet.")

    st.markdown("""
    <div class='bs-footer'>
      👑 BloodSetu Admin Panel · Parul University · BCA Mini Project-II<br>
      📧 bloodsetu.help@gmail.com
    </div>
    """, unsafe_allow_html=True)