import streamlit as st

from admin_portal import admin_login_page, admin_dashboard
from bookflow import BookFlowApp, show_books_page

st.set_page_config(
    page_title="BookFlow Admin Portal",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="expanded",
)


def _ensure_app_instance():
    if "app" not in st.session_state:
        st.session_state.app = BookFlowApp()
    elif not (
        hasattr(st.session_state.app, "get_active_reservation")
        and hasattr(st.session_state.app, "create_reservation")
    ):
        st.session_state.app = BookFlowApp()


def _ensure_session_defaults():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "user" not in st.session_state:
        st.session_state.user = None
    if "role" not in st.session_state:
        st.session_state.role = None
    if "page" not in st.session_state:
        st.session_state.page = "admin_login"


_definitions_initialized = False


def _prepare_state():
    global _definitions_initialized
    if not _definitions_initialized:
        _ensure_app_instance()
        _definitions_initialized = True
    _ensure_session_defaults()


def _logout_admin():
    st.session_state.logged_in = False
    st.session_state.user = None
    st.session_state.role = None
    st.session_state.page = "admin_login"
    st.rerun()


def main():
    _prepare_state()

    if not st.session_state.logged_in or st.session_state.role != "admin":
        st.session_state.role = None
        if st.session_state.page != "admin_login":
            st.session_state.page = "admin_login"
        admin_login_page()
        return

    with st.sidebar:
        st.markdown(
            f"""
            <div style='background: #1e1e1e; padding: 0.8rem; border-radius: 8px; margin-bottom: 1rem;
                        border-left: 3px solid #6C0345;'>
                <p style='margin: 0; font-size: 1rem; font-weight: 600; color: #ffffff;'>👤 {st.session_state.user['name']}</p>
                <p style='margin: 0.2rem 0 0 0; font-size: 0.8rem; color: #b0b0b0;'>Administrator • {st.session_state.user['id']}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        menu = st.radio(
            "",
            ["📊 Dashboard", "📚 Books", "🚪 Logout"],
            label_visibility="collapsed",
        )

        if menu == "🚪 Logout":
            _logout_admin()

    if menu == "📊 Dashboard":
        admin_dashboard()
    elif menu == "📚 Books":
        show_books_page()


if __name__ == "__main__":
    main()
