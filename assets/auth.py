import streamlit as st
import bcrypt

def inject_login_css():
    st.markdown(
        """
        <style>
        /* Input fields */
        input[type="text"], input[type="password"] {
            background-color: #ffffff !important;
            color: #000000 !important;
            border: 1px solid #cccccc;
            border-radius: 6px;
            padding: 0.5rem;
        }

        /* Placeholder */
        input::placeholder {
            color: #888888 !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )


def check_login():
    if st.session_state.get("authenticated"):
        return True
    inject_login_css()

    st.title("Acceso restringido")

    username = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")

    if st.button("Ingresar"):
        users = st.secrets["auth"]["users"]

        if username in users:
            stored_hash = users[username].encode()
            if bcrypt.checkpw(password.encode(), stored_hash):
                st.session_state.authenticated = True
                st.session_state.user = username
                st.rerun()

        st.error("Credenciales incorrectas")

    return False
