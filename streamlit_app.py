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
  .block-container {padding-top: 1.5rem; padding-bottom: 2rem;}
  [data-testid="stMetric"] {background:#fff;border:1px solid #e8edf5;padding:16px 18px;border-radius:14px;box-shadow:0 2px 10px rgba(30,50,80,.035)}
  [data-testid="stSidebar"] {border-right:1px solid #edf0f6;}
  h1,h2,h3 {color:#243147;}
</style>
""", unsafe_allow_html=True)

st.sidebar.markdown("## 📊 Taqi Motos")
st.sidebar.caption("Painel financeiro")
add_session_controls(role)
can_edit = role == "owner"

pages = [
    st.Page("app_pages/dashboard.py", title="Visão financeira", icon="📈", default=True),
    st.Page("app_pages/products.py", title="Produtos", icon="📦"),
]
if can_edit:
    pages.extend([
        st.Page("app_pages/entry.py", title="Cadastrar dados", icon="✍️"),
        st.Page("app_pages/import_excel.py", title="Importar planilha", icon="📥"),
    ])
navigation = st.navigation(pages, position="sidebar")
navigation.run()

st.sidebar.divider()
st.sidebar.caption("PostgreSQL na nuvem" if db.engine.dialect.name != "sqlite" else "Demonstração local • SQLite")
