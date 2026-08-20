"""
auth.py — BloodSetu Authentication
Login, Register, Session Management
"""

import streamlit as st
from database import register_user, login_user, get_donor_by_user

ADMIN_USERNAME = "bloodsetu_admin"
ADMIN_PASSWORD = "BloodSetu@2026"


def init_session():
    """Initialize all session state variables."""
    defaults = {
        "logged_in": False,
        "user": None,
        "role": None,
        "donor_data": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def is_logged_in() -> bool:
    return st.session_state.get("logged_in", False)


def current_role() -> str:
    return st.session_state.get("role", "")


def current_user() -> dict:
    return st.session_state.get("user", {})


def logout():
    st.session_state.logged_in = False
    st.session_state.user = None
    st.session_state.role = None
    st.session_state.donor_data = None


def login_form(role_hint: str = ""):
    """Render a login form. Returns True if login successful."""
    st.markdown("### 🔑 Login")
    username = st.text_input("Username", key=f"login_user_{role_hint}")
    password = st.text_input("Password", type="password", key=f"login_pass_{role_hint}")

    if st.button("Login", key=f"login_btn_{role_hint}", use_container_width=True):
        # Admin check
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            st.session_state.logged_in = True
            st.session_state.role = "admin"
            st.session_state.user = {"username": ADMIN_USERNAME, "role": "admin"}
            st.success("✅ Welcome, Admin!")
            st.rerun()
            return True

        user = login_user(username, password)
        if user:
            st.session_state.logged_in = True
            st.session_state.user = user
            st.session_state.role = user["role"]
            if user["role"] == "donor":
                donor = get_donor_by_user(user["id"])
                st.session_state.donor_data = donor
            st.success(f"✅ Welcome back, {username}!")
            st.rerun()
            return True
        else:
            st.error("❌ Invalid username or password.")
            return False
    return False


def register_form(role: str):
    """Render a registration form for a given role."""
    st.markdown(f"### 📝 Register as {role.title()}")
    username = st.text_input("Choose Username", key=f"reg_user_{role}")
    password = st.text_input("Choose Password", type="password", key=f"reg_pass_{role}")
    phone    = st.text_input("Phone Number (10 digits)", key=f"reg_phone_{role}")

    if st.button(f"Register as {role.title()}", key=f"reg_btn_{role}", use_container_width=True):
        if not username or not password or not phone:
            st.warning("Please fill all fields.")
            return False, None
        if len(phone) != 10 or not phone.isdigit():
            st.warning("Enter a valid 10-digit phone number.")
            return False, None
        success, user_id = register_user(username, password, role, phone)
        if success:
            st.success("✅ Account created! Please complete your profile below.")
            return True, user_id
        else:
            st.error("❌ Username already exists. Try another.")
            return False, None
    return False, None


def require_login(role: str = None):
    """
    Show login wall if not logged in.
    Optionally restrict to a specific role.
    Returns True if user has access.
    """
    init_session()
    if not is_logged_in():
        st.warning("🔐 Please login to access this page.")
        login_form(role or "")
        return False
    if role and current_role() != role and current_role() != "admin":
        st.error(f"❌ This page is only for {role}s.")
        return False
    return True

