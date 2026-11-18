
"""
User Management

Professional administration interface for AVIONAV users.
"""

import streamlit as st
import pandas as pd
from html import escape

from components.sidebar import show as render_sidebar
from components.header import show as render_header
from components.cards import info_card, alert_card, section_title
from components.theme import COLORS
from utils.auth import require_administrator, get_role_display_name
from utils.api import get_users, create_user, update_user, disable_user, enable_user


def _filter_users(users, search, role_filter):
    if not users:
        return []

    filtered = users

    if role_filter and role_filter != "All":
        filtered = [u for u in filtered if u.get("role") == role_filter]

    if search:
        s = search.lower()
        filtered = [
            u for u in filtered
            if s in u.get("username", "").lower()
            or s in u.get("email", "").lower()
        ]

    return filtered


def _get_users_cached():
    """Load users once and cache them in session state."""
    if "users_list" not in st.session_state:
        st.session_state.users_list = get_users() or []

    return st.session_state.users_list


def _clear_users_cache():
    """Invalidate the cached user list."""
    st.session_state.pop("users_list", None)


def show() -> None:
    require_administrator()

    render_sidebar("users")
    render_header(
        "User Management",
        "Create, view, update and disable user accounts"
    )

    # User Management page styling: enforce readable text in dark theme.
    st.markdown(
        f"""
        <style>
        /* Labels and disabled/enabled input values */
        div[data-testid="stMain"] div[data-testid="stTextInput"] label,
        div[data-testid="stMain"] div[data-testid="stTextArea"] label,
        div[data-testid="stMain"] div[data-testid="stSelectbox"] label,
        div[data-testid="stMain"] div[data-testid="stTextInput"] label *,
        div[data-testid="stMain"] div[data-testid="stTextArea"] label *,
        div[data-testid="stMain"] div[data-testid="stSelectbox"] label * {{
            color: #FFFFFF !important;
            -webkit-text-fill-color: #FFFFFF !important;
            opacity: 1 !important;
        }}

        div[data-testid="stMain"] input,
        div[data-testid="stMain"] textarea,
        div[data-testid="stMain"] input:disabled,
        div[data-testid="stMain"] textarea:disabled {{
            color: #FFFFFF !important;
            -webkit-text-fill-color: #FFFFFF !important;
            opacity: 1 !important;
        }}

        div[data-testid="stMain"] input::placeholder,
        div[data-testid="stMain"] textarea::placeholder {{
            color: #FFFFFF !important;
            -webkit-text-fill-color: #FFFFFF !important;
            opacity: 0.75 !important;
        }}

        /* Expander headings: white text on navy, including collapsed state */
        div[data-testid="stMain"] [data-testid="stExpander"] details > summary,
        div[data-testid="stMain"] [data-testid="stExpander"] details > summary p,
        div[data-testid="stMain"] [data-testid="stExpander"] details > summary span,
        div[data-testid="stMain"] [data-testid="stExpander"] details > summary div,
        div[data-testid="stMain"] [data-testid="stExpander"] details > summary svg {{
            color: #FFFFFF !important;
            fill: #FFFFFF !important;
            -webkit-text-fill-color: #FFFFFF !important;
            opacity: 1 !important;
        }}

        div[data-testid="stMain"] [data-testid="stExpander"] details > summary {{
            background: {COLORS['card']} !important;
            border: 1px solid {COLORS['border']} !important;
            border-radius: 6px !important;
        }}

        div[data-testid="stMain"] [data-testid="stExpander"] details > summary:hover {{
            background: {COLORS['card']} !important;
        }}

        /* Main buttons and form buttons, including disabled administrator actions */
        div[data-testid="stMain"] div[data-testid="stButton"] button,
        div[data-testid="stMain"] div[data-testid="stButton"] button *,
        div[data-testid="stMain"] div[data-testid="stFormSubmitButton"] button,
        div[data-testid="stMain"] div[data-testid="stFormSubmitButton"] button * {{
            color: #FFFFFF !important;
            -webkit-text-fill-color: #FFFFFF !important;
            opacity: 1 !important;
        }}

        div[data-testid="stMain"] div[data-testid="stButton"] button:disabled,
        div[data-testid="stMain"] div[data-testid="stButton"] button[aria-disabled="true"] {{
            background-color: {COLORS['card']} !important;
            border-color: {COLORS['border']} !important;
            cursor: not-allowed !important;
        }}

        div[data-testid="stMain"] div[data-testid="stButton"] button:disabled *,
        div[data-testid="stMain"] div[data-testid="stButton"] button[aria-disabled="true"] * {{
            color: #FFFFFF !important;
            -webkit-text-fill-color: #FFFFFF !important;
            opacity: 1 !important;
        }}

        div[data-testid="stMain"] [data-testid="stExpander"] details > div {{
            background-color: {COLORS['card']} !important;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

    users = _get_users_cached()

    tab1, tab2, tab3 = st.tabs([
        "● VIEW USERS",
        "● CREATE USER",
        "● MANAGE USER"
    ])

    # --------------------------------------------------
    # TAB 1: VIEW USERS
    # --------------------------------------------------

    with tab1:
        section_title("All Users")

        if not users:
            info_card("No Users", "No user accounts found.")

        else:
            col1, col2 = st.columns([2, 1])

            with col1:
                search = st.text_input(
                    "Search",
                    placeholder="Search by username or email",
                    key="users_search",
                )

            with col2:
                role_filter = st.selectbox(
                    "Role",
                    [
                        "All",
                        "administrator",
                        "maintenance_engineer",
                        "drone_operator"
                    ],
                    format_func=lambda x: (
                        "All" if x == "All"
                        else get_role_display_name(x)
                    ),
                    key="users_role_filter",
                )

            filtered = _filter_users(users, search, role_filter)

            if not filtered:
                alert_card(
                    "No users match the selected filters",
                    "info"
                )

            else:
                df = pd.DataFrame(filtered)

                if "disabled" not in df.columns:
                    st.error(
                        "User data is missing the required 'disabled' "
                        "field. The backend response may be inconsistent."
                    )

                else:
                    df["role_display"] = df["role"].map(
                        get_role_display_name
                    )

                    df["status"] = df["disabled"].apply(
                        lambda x: "Disabled" if x else "Active"
                    )

                    st.dataframe(
                        df[
                            [
                                "username",
                                "email",
                                "role_display",
                                "status"
                            ]
                        ],
                        use_container_width=True,
                    )

    # --------------------------------------------------
    # TAB 2: CREATE USER
    # --------------------------------------------------

    with tab2:
        section_title("Create New User")

        if "create_user_success" in st.session_state:
            st.success(st.session_state["create_user_success"])
            del st.session_state["create_user_success"]

        form_counter = st.session_state.get(
            "create_form_counter", 0
        )

        with st.form(f"create_user_form_{form_counter}"):

            col1, col2 = st.columns(2)

            with col1:
                username = st.text_input(
                    "Username",
                    placeholder="Enter username",
                    key=f"create_username_{form_counter}"
                )

                email = st.text_input(
                    "Email",
                    placeholder="Enter email",
                    key=f"create_email_{form_counter}"
                )

            with col2:
                password = st.text_input(
                    "Password",
                    type="password",
                    placeholder="Enter password",
                    key=f"create_password_{form_counter}"
                )

                role = st.selectbox(
                    "Role",
                    [
                        "maintenance_engineer",
                        "drone_operator"
                    ],
                    format_func=get_role_display_name,
                    key=f"create_role_{form_counter}",
                )

            submitted = st.form_submit_button(
                "CREATE USER",
                type="primary"
            )

            if submitted:
                if username and email and password and role:

                    result = create_user(
                        username,
                        email,
                        password,
                        role
                    )

                    if result:
                        _clear_users_cache()

                        st.session_state["create_form_counter"] = (
                            form_counter + 1
                        )

                        st.session_state["create_user_success"] = (
                            f"User '{result.get('username', username)}' "
                            "created successfully."
                        )

                        st.rerun()

                    else:
                        st.error("Failed to create user")

                else:
                    st.warning("Please fill in all fields")

    # --------------------------------------------------
    # TAB 3: MANAGE USER
    # --------------------------------------------------

    with tab3:
        section_title("Manage User")

        if "manage_user_success" in st.session_state:
            st.success(st.session_state["manage_user_success"])
            del st.session_state["manage_user_success"]

        if not users:
            info_card("No Users", "No users to manage.")

        else:
            user_options = {
                f"{u['username']} ({u['email']})": u
                for u in users
            }

            selected = st.selectbox(
                "Select user",
                list(user_options.keys()),
                key="select_user"
            )

            if selected:
                user = user_options[selected]

                # Protect the administrator account
                is_admin = user["username"] == "admin"

                col1, col2 = st.columns(2)

                # USER DETAILS: retain the original card appearance and use white text.
                with col1:
                    status = "Disabled" if user.get("disabled") else "Active"
                    username_text = escape(str(user.get("username", "")))
                    email_text = escape(str(user.get("email", "")))
                    role_text = escape(get_role_display_name(user.get("role", "")))
                    status_text = escape(status)
                    st.markdown(
                        f"""
                        <div style="
                            background: {COLORS['card']};
                            border: 1px solid {COLORS['border']};
                            border-radius: 8px;
                            padding: 20px;
                            min-height: 220px;
                        ">
                            <div style="color:#FFFFFF;font-size:12px;text-transform:uppercase;
                                        font-weight:600;margin-bottom:18px;">
                                USER DETAILS
                            </div>
                            <p style="color:#FFFFFF;margin:10px 0;">
                                <strong>Username:</strong> {username_text}
                            </p>
                            <p style="color:#FFFFFF;margin:10px 0;">
                                <strong>Email:</strong> {email_text}
                            </p>
                            <p style="color:#FFFFFF;margin:10px 0;">
                                <strong>Role:</strong> {role_text}
                            </p>
                            <p style="color:#FFFFFF;margin:10px 0;">
                                <strong>Status:</strong> {status_text}
                            </p>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                # USER ACTIONS
                with col2:

                    # UPDATE USER
                    with st.expander("Update User"):

                        new_email = st.text_input(
                            "New Email",
                            user["email"],
                            key=f"update_email_{user['id']}",
                            disabled=is_admin
                        )

                        role_options = [
                            "maintenance_engineer",
                            "drone_operator"
                        ]

                        new_role = st.selectbox(
                            "New Role",
                            role_options,
                            index=(
                                role_options.index(user["role"])
                                if user["role"] in role_options
                                else 0
                            ),
                            format_func=get_role_display_name,
                            key=f"update_role_{user['id']}",
                            disabled=(
                                is_admin
                                or user["role"] not in role_options
                            ),
                        )

                        if st.button(
                            "UPDATE",
                            key=f"update_user_{user['id']}",
                            use_container_width=True,
                            disabled=is_admin
                        ):
                            result = update_user(
                                user["id"],
                                email=new_email,
                                role=new_role
                            )

                            if result:
                                _clear_users_cache()
                                st.success("User updated")
                                st.rerun()

                            else:
                                st.error("Update failed")

                    # DISABLE OR ENABLE USER
                    if not user.get("disabled"):

                        with st.expander("Disable User"):

                            reason = st.text_area(
                                "Reason",
                                placeholder="Optional reason",
                                key=f"disable_reason_{user['id']}",
                                disabled=is_admin
                            )

                            if st.button(
                                "DISABLE ACCOUNT",
                                key=f"disable_user_{user['id']}",
                                use_container_width=True,
                                disabled=is_admin
                            ):
                                result = disable_user(
                                    user["id"],
                                    disabled=True,
                                    reason=reason
                                )

                                if result:
                                    _clear_users_cache()

                                    st.session_state[
                                        "manage_user_success"
                                    ] = (
                                        f"User '{user['username']}' "
                                        "has been disabled successfully."
                                    )

                                    st.rerun()

                                else:
                                    st.error("Disable failed")

                    else:
                        with st.expander("Enable User"):

                            if st.button(
                                "ENABLE ACCOUNT",
                                key=f"enable_user_{user['id']}",
                                use_container_width=True
                            ):
                                result = enable_user(user["id"])

                                if result:
                                    _clear_users_cache()

                                    st.session_state[
                                        "manage_user_success"
                                    ] = (
                                        f"User '{user['username']}' "
                                        "has been enabled successfully."
                                    )

                                    st.rerun()

                                else:
                                    st.error("Enable failed")
