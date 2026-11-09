import streamlit as st

import db
from auth import add_session_controls, current_role

st.set_page_config(page_title="Taqi Motos | Financeiro", page_icon="📊", layout="wide", initial_sidebar_state="expanded")
role = current_role()
st.session_state["app_role"] = role
db.initialize()
db.seed_initial_data()

if "app_dark_mode" not in st.session_state:
    st.session_state["app_dark_mode"] = False
dark_mode = bool(st.session_state["app_dark_mode"])

theme = {
    "mode": "dark" if dark_mode else "light",
    "page": "#0b1220" if dark_mode else "#f7f9fc",
    "text": "#e5eaf2" if dark_mode else "#243147",
    "header": "rgba(11,18,32,.96)" if dark_mode else "rgba(247,249,252,.96)",
    "sidebar": "#111a2b" if dark_mode else "#ffffff",
    "border": "#29384f" if dark_mode else "#e8edf5",
    "card": "#121d30" if dark_mode else "#ffffff",
    "heading": "#f8fafc" if dark_mode else "#243147",
    "muted": "#c5cfdd" if dark_mode else "#526078",
    "input": "#172338" if dark_mode else "#ffffff",
}
theme_css = """
<style>
  :root { color-scheme: __MODE__; }
  .block-container {padding-top: 1.5rem; padding-bottom: 2rem;}
  .stApp, [data-testid="stAppViewContainer"] {background:__PAGE__;color:__TEXT__;}
  [data-testid="stHeader"] {background:__HEADER__;}
  [data-testid="stSidebar"] {background:__SIDEBAR__;border-right:1px solid __BORDER__;}
  [data-testid="stMetric"] {background:__CARD__;border:1px solid __BORDER__;padding:16px 18px;border-radius:14px;box-shadow:0 2px 10px rgba(30,50,80,.08);}
  h1,h2,h3 {color:__HEADING__;}
  p, label, [data-testid="stCaptionContainer"], [data-testid="stMarkdownContainer"] {color:__MUTED__;}
  [data-baseweb="select"] > div, input, textarea {background:__INPUT__;color:__TEXT__;}
  [data-testid="stDataFrame"], [data-testid="stTable"] {background:__CARD__;}
  .st-key-theme_toggle button {border:1px solid __BORDER__;background:__INPUT__;color:__TEXT__;}
</style>
"""
for token, key in [
    ("__MODE__", "mode"), ("__PAGE__", "page"), ("__TEXT__", "text"),
    ("__HEADER__", "header"), ("__SIDEBAR__", "sidebar"),
    ("__BORDER__", "border"), ("__CARD__", "card"),
    ("__HEADING__", "heading"), ("__MUTED__", "muted"), ("__INPUT__", "input"),
]:
    theme_css = theme_css.replace(token, theme[key])
st.markdown(theme_css, unsafe_allow_html=True)

st.sidebar.markdown("## 📊 Taqi Motos")
st.sidebar.caption("Painel financeiro")
add_session_controls(role)
if st.sidebar.button(
    "🌙 Noturno" if dark_mode else "☀️ Claro",
    key="theme_toggle",
    width="stretch",
    help="Alternar entre tema claro e noturno",
):
    st.session_state["app_dark_mode"] = not dark_mode
    st.rerun()
can_edit = role == "owner"

pages = [
    st.Page("app_pages/dashboard.py", title="Visão financeira", icon="📈", default=True),
    st.Page("app_pages/dfc.py", title="Lançamento", icon="💰"),
    st.Page("app_pages/products.py", title="Produtos", icon="📦"),
    st.Page("app_pages/analysis.py", title="Gráficos financeiros", icon="📊"),
]
if can_edit:
    pages.extend([
    
        st.Page("app_pages/import_excel.py", title="Importar planilha", icon="📥"),
        st.Page("app_pages/reset_data.py", title="Reiniciar dados", icon="🧹"),
    ])
navigation = st.navigation(pages, position="sidebar")
navigation.run()

st.sidebar.divider()
st.sidebar.caption("PostgreSQL na nuvem" if db.engine.dialect.name != "sqlite" else "Demonstração local • SQLite")
