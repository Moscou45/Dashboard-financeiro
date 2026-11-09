import streamlit as st

import db
from auth import add_session_controls, current_role

st.set_page_config(page_title="Taqi Motos | Financeiro", page_icon="📊", layout="wide", initial_sidebar_state="expanded")
role = current_role()
st.session_state["app_role"] = role
db.initialize()
db.seed_initial_data()

st.markdown("""
<style>
  :root { color-scheme: dark; }
  .block-container {padding-top: 1.5rem; padding-bottom: 2rem;}
  .stApp, [data-testid="stAppViewContainer"] {background:#0b1220;color:#e5eaf2;}
  [data-testid="stHeader"] {background:rgba(11,18,32,.96);}
  [data-testid="stSidebar"] {background:#111a2b;border-right:1px solid #29384f;}
  [data-testid="stMetric"] {background:#121d30;border:1px solid #29384f;padding:16px 18px;border-radius:14px;box-shadow:0 2px 10px rgba(30,50,80,.08);}
  h1,h2,h3 {color:#f8fafc;}
  p, label, [data-testid="stCaptionContainer"], [data-testid="stMarkdownContainer"] {color:#c5cfdd;}
  [data-baseweb="select"] > div, input, textarea {background:#172338;color:#e5eaf2;}
  [data-testid="stDataFrame"], [data-testid="stTable"] {background:#121d30;}
  .st-key-theme_toggle button {border:1px solid #29384f;background:#172338;color:#e5eaf2;}
</style>
""", unsafe_allow_html=True)

st.sidebar.markdown("## 📊 Taqi Motos")
st.sidebar.caption("Painel financeiro")
add_session_controls(role)
if "app_dark_mode" not in st.session_state:
    st.session_state["app_dark_mode"] = False
dark_mode = bool(st.session_state["app_dark_mode"])
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
