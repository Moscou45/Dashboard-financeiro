from __future__ import annotations

import os

import streamlit as st


def _secrets():
    try:
        return st.secrets
    except Exception:
        return {}


def is_production() -> bool:
    secrets = _secrets()
    app_env = os.getenv("APP_ENV") or secrets.get("APP_ENV", "")
    database = secrets.get("database", {}) if hasattr(secrets, "get") else {}
    return str(app_env).casefold() == "production" or bool(os.getenv("DATABASE_URL")) or bool(database.get("url"))


def _auth_configured() -> bool:
    auth = _secrets().get("auth", {})
    return bool(auth.get("client_id") and auth.get("client_secret") and auth.get("server_metadata_url")
                and auth.get("redirect_uri") and auth.get("cookie_secret"))


def current_role() -> str:
    if _auth_configured():
        if not st.user.is_logged_in:
            st.title("Painel financeiro Taqi Motos")
            st.write("Entre com a conta Google autorizada para acessar o painel.")
            st.button("Entrar com Google", type="primary", on_click=st.login)
            st.stop()
        email = str(st.user.get("email", "")).strip().casefold()
        authorization = _secrets().get("authorization", {})
        owner = str(authorization.get("owner_email", "")).strip().casefold()
        viewer = str(authorization.get("viewer_email", "")).strip().casefold()
        if email and email == owner:
            return "owner"
        if email and email == viewer:
            return "viewer"
        st.error("Esta conta não está autorizada a acessar o painel.")
        st.button("Sair", on_click=st.logout)
        st.stop()

    if is_production():
        st.error("O login online ainda não foi configurado. O acesso foi bloqueado por segurança.")
        st.stop()

    selected = st.sidebar.radio("Perfil local de demonstração", ["Você — edição", "Patrão — somente leitura"])
    st.session_state["app_role"] = "owner" if selected.startswith("Você") else "viewer"
    return st.session_state["app_role"]


def require_editor() -> None:
    if st.session_state.get("app_role") != "owner":
        st.error("Esta página está disponível apenas para o proprietário do painel.")
        st.stop()


def add_session_controls(role: str) -> None:
    if _auth_configured() and st.user.is_logged_in:
        st.sidebar.caption(f"Acesso: {'proprietário' if role == 'owner' else 'somente leitura'}")
        st.sidebar.button("Sair da conta", on_click=st.logout)
