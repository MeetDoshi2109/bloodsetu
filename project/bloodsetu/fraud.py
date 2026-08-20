"""
fraud.py — BloodSetu Fraud Prevention System
Report fake requests, admin block, appeal via email
"""

import streamlit as st
from database import report_fake, get_all_reports, resolve_report, block_user_by_phone


REPORT_REASONS = [
    "Wrong phone number",
    "Wrong location / fake address",
    "Nobody responded to calls",
    "Suspicious / prank request",
    "Duplicate request",
    "Other",
]


def show_report_button(reported_by_type: str, reported_by_id: int, context_key: str = ""):
    """Show a report fake request button for providers."""
    with st.expander("🚩 Report Wrong / Fake Request"):
        st.markdown("**Did this seeker give wrong details?**")
        phone = st.text_input(
            "Seeker's phone number to report",
            key=f"report_phone_{context_key}"
        )
        reason = st.selectbox(
            "Reason for reporting",
            REPORT_REASONS,
            key=f"report_reason_{context_key}"
        )
        if st.button("🚩 Submit Report", key=f"report_btn_{context_key}"):
            if phone:
                report_fake(phone, reported_by_type, reported_by_id, reason)
                st.success("✅ Report submitted. Admin will review within 24 hours.")
            else:
                st.warning("Please enter the phone number to report.")


def show_blocked_screen():
    """Show blocked user screen with appeal email."""
    st.error("🚫 Your access has been restricted.")
    st.markdown("""
    <div style='background:rgba(192,57,43,0.1);border:1px solid #c0392b;
    border-radius:12px;padding:20px;margin-top:12px;text-align:center'>
        <h3 style='color:#e74c3c'>Access Restricted</h3>
        <p style='color:#ccc'>We understand mistakes happen.<br>
        If this was a genuine mistake, please reach out to us.</p>
        <br>
        <p style='color:#f0c040;font-size:18px'>📧 bloodsetu.help@gmail.com</p>
        <br>
        <p style='color:#aaa;font-size:13px'>
        BloodSetu exists to save lives — including yours. ❤️<br>
        We will review and respond within 24 hours.</p>
    </div>
    """, unsafe_allow_html=True)


def admin_fraud_panel():
    """Admin panel for reviewing and resolving fraud reports."""
    st.markdown("### 🛡️ Fraud Reports")
    reports = get_all_reports()

    if not reports:
        st.info("No reports yet.")
        return

    pending = [r for r in reports if r["admin_action"] == "Pending"]
    resolved = [r for r in reports if r["admin_action"] != "Pending"]

    st.markdown(f"**{len(pending)} Pending · {len(resolved)} Resolved**")

    if pending:
        st.markdown("#### ⚠️ Pending Reports")
        for r in pending:
            with st.container():
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.markdown(f"""
                    📞 **{r['reported_phone']}** · Reported by: {r['reported_by_type']}
                    Reason: {r['reason']} · At: {r['reported_at'][:16]}
                    """)
                with col2:
                    if st.button("✅ Block", key=f"block_{r['id']}"):
                        block_user_by_phone(r["reported_phone"])
                        resolve_report(r["id"], "Blocked")
                        st.success("User blocked.")
                        st.rerun()
                with col3:
                    if st.button("❌ Ignore", key=f"ignore_{r['id']}"):
                        resolve_report(r["id"], "Ignored")
                        st.info("Report ignored.")
                        st.rerun()
                st.divider()

    if resolved:
        with st.expander(f"📋 Resolved Reports ({len(resolved)})"):
            for r in resolved:
                st.markdown(
                    f"📞 {r['reported_phone']} · "
                    f"Action: **{r['admin_action']}** · "
                    f"{r.get('resolved_at','')[:16]}"
                )