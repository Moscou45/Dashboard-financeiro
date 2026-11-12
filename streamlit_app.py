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
  [data-testid="stSelectbox"] [role="group"], [data-testid="stMultiSelect"] [role="group"] {background:__INPUT__;color:__TEXT__;border-color:__BORDER__;}
  [data-testid="stSidebar"] [data-testid="stButton"] button {background:__INPUT__;color:__TEXT__;border-color:__BORDER__;}
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
brand_css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500&family=Poppins:wght@700&display=swap');
:root{color-scheme:__MODE__;}
.stApp,.stApp *{font-family:'Inter',sans-serif!important;font-weight:400;}
/* Preserve Streamlit's ligature font for Material Symbols. */
[data-testid="stIconMaterial"],[data-testid="stIconMaterial"] *{
  font-family:"Material Symbols Rounded"!important;
  font-weight:normal!important;font-style:normal!important;
  font-feature-settings:"liga";-webkit-font-feature-settings:"liga";
  -webkit-font-smoothing:antialiased;
}
h1,h2,h3,[data-testid="stMetricLabel"],[data-testid="stMetricValue"],[data-testid="stSubheader"]{font-family:'Poppins',sans-serif!important;font-weight:700!important;letter-spacing:-.02em;}
[data-testid="stTabs"] button,[data-testid="stSidebarNav"] a{font-family:'Inter',sans-serif!important;font-weight:500!important;}
.block-container{max-width:1600px;padding-top:2rem;padding-bottom:3rem;}
.stApp,[data-testid="stAppViewContainer"]{background:__PAGE__;color:__TEXT__;}
[data-testid="stSidebar"]{background:#082f49;border-right:1px solid rgba(255,255,255,.08);}
[data-testid="stSidebar"] *{color:#e8f2fb;}
[data-testid="stSidebar"] label,[data-testid="stSidebar"] [data-testid="stWidgetLabel"]{color:#d5e4ee!important;}
[data-testid="stSidebar"] [data-testid="stCaptionContainer"]{color:#a9c1d4!important;}
[data-testid="stSidebar"] [data-baseweb="select"]>div{background:#142a3d!important;border-color:#36536b!important;}
[data-testid="stSidebar"] [data-baseweb="select"] *,[data-testid="stSidebar"] [data-baseweb="select"] input{color:#f4f8fb!important;-webkit-text-fill-color:#f4f8fb!important;}
[data-testid="stSidebar"] [data-testid="stButton"] button{background:rgba(255,255,255,.08);color:#fff;border:1px solid rgba(255,255,255,.16);border-radius:10px;}
[data-testid="stSidebarNav"] a{border-radius:9px;margin:2px 4px;transition:background .18s ease,color .18s ease;}
[data-testid="stSidebarNav"] a[aria-current="page"]{background:rgba(45,212,191,.18);color:#7debdc;font-weight:650;}
[data-testid="stMetric"]{background:__CARD__;border:1px solid __BORDER__;padding:18px 20px;border-radius:16px;box-shadow:0 8px 24px rgba(15,35,65,.06);}
[data-testid="stMetricLabel"]{color:__MUTED__!important;}[data-testid="stMetricValue"]{color:__HEADING__!important;}
h1,h2,h3{color:__HEADING__!important;}
p,label,[data-testid="stCaptionContainer"],[data-testid="stMarkdownContainer"]{color:__MUTED__;}
[data-testid="stForm"] [data-baseweb="input"]>div,
[data-testid="stForm"] [data-baseweb="select"]>div,
[data-testid="stForm"] input,
[data-testid="stForm"] textarea,
[data-testid="stForm"] [data-testid="stDateInput"]>div,
[data-testid="stForm"] [data-testid="stDateInput"] input,
[data-baseweb="input"]>div,[data-baseweb="select"]>div,input,textarea{
  background-color:__INPUT__!important;border-color:__BORDER__!important;
  transition:background-color .22s ease,color .22s ease,border-color .22s ease;
}
[data-testid="stForm"] input,[data-testid="stForm"] textarea,
[data-testid="stForm"] [data-baseweb="select"] *,
[data-baseweb="input"] input,[data-baseweb="select"] *,input,textarea{
  color:__TEXT__!important;-webkit-text-fill-color:__TEXT__!important;
}
[data-testid="stForm"] [data-baseweb="select"] svg,
[data-testid="stForm"] [data-testid="stDateInput"] svg{fill:__MUTED__!important;color:__MUTED__!important;}
input::placeholder,textarea::placeholder{color:__MUTED__!important;opacity:1;}

/* Keep date and numeric controls aligned with the active app theme. */
[data-testid="stDateInput"] [data-baseweb="input"],
[data-testid="stDateInput"] [data-baseweb="input"]>div,
[data-testid="stDateInput"] input,
[data-testid="stNumberInput"] [data-baseweb="input"],
[data-testid="stNumberInput"] [data-baseweb="input"]>div,
[data-testid="stNumberInput"] input{
  background-color:__INPUT__!important;color:__TEXT__!important;
  -webkit-text-fill-color:__TEXT__!important;border-color:__BORDER__!important;
}
[data-testid="stNumberInput"] button{
  background-color:__INPUT__!important;color:__TEXT__!important;
  border-color:__BORDER__!important;
}
[data-testid="stDateInput"] svg,[data-testid="stNumberInput"] svg{
  fill:__MUTED__!important;color:__MUTED__!important;
}
/* Tab overflow controls use the same surface as the tabs. */
[data-testid="stTabs"] button[aria-label="Scroll tabs right"],
[data-testid="stTabs"] button[aria-label="Scroll tabs left"]{
  background:__CARD__!important;color:__TEXT__!important;
  border:0!important;box-shadow:none!important;
}
[data-testid="stTabs"] button[aria-label^="Scroll tabs"] svg{
  fill:__TEXT__!important;color:__TEXT__!important;
}

/* Dropdown menus are rendered in a portal, so style them independently of the widget. */
[data-baseweb="popover"],[data-baseweb="popover"]>div,[data-baseweb="menu"],[role="listbox"]{
  background-color:__CARD__!important;color:__TEXT__!important;
  border:1px solid __BORDER__!important;border-radius:10px;
  box-shadow:0 12px 32px rgba(0,0,0,.22);
}
[data-baseweb="popover"] [role="option"],[role="listbox"] [role="option"]{
  background-color:__CARD__!important;color:__TEXT__!important;
  -webkit-text-fill-color:__TEXT__!important;
}
[data-baseweb="popover"] [role="option"]:hover,
[data-baseweb="popover"] [role="option"][aria-selected="true"],
[role="listbox"] [role="option"]:hover,
[role="listbox"] [role="option"][aria-selected="true"]{
  background-color:__INPUT__!important;color:__HEADING__!important;
  -webkit-text-fill-color:__HEADING__!important;
}
[data-baseweb="popover"] [data-highlighted="true"]{
  background-color:__INPUT__!important;color:__HEADING__!important;
}
[data-baseweb="popover"] [data-baseweb="menu"] *{color:__TEXT__!important;}

[data-testid="stForm"],[data-testid="stVerticalBlockBorderWrapper"]{border-color:__BORDER__!important;border-radius:16px;}
[data-testid="stForm"]{background:__CARD__;padding:1rem 1.15rem;transition:background-color .22s ease,border-color .22s ease;}
[data-testid="stDataFrame"],[data-testid="stTable"]{background:__CARD__;border:1px solid __BORDER__;border-radius:12px;overflow:hidden;transition:background-color .22s ease,border-color .22s ease;}
[data-testid="stPlotlyChart"]{background:__CARD__;border:1px solid __BORDER__;border-radius:16px;padding:8px 8px 2px;}
[data-testid="stButton"] button,[data-testid="stDownloadButton"] button,[data-testid="stFormSubmitButton"] button{border-radius:10px;transition:all .16s ease;}
[data-testid="stFormSubmitButton"] button[kind="primary"]{background:#0f9f91;border-color:#0f9f91;color:#fff;font-weight:650;}
.st-key-theme_toggle button{border:1px solid rgba(255,255,255,.18);background:rgba(255,255,255,.08);color:white;}
@media(max-width:700px){.block-container{padding:1rem .8rem 2rem;}h1{font-size:1.65rem!important;}}
</style>
"""
for token,key in [("__MODE__","mode"),("__PAGE__","page"),("__TEXT__","text"),("__CARD__","card"),("__BORDER__","border"),("__MUTED__","muted"),("__HEADING__","heading"),("__INPUT__","input")]:
    brand_css=brand_css.replace(token,theme[key])
st.markdown(brand_css,unsafe_allow_html=True)

can_edit = role == "owner"

navigation = st.navigation(
    {
        "PAINEL": [st.Page("app_pages/dashboard.py", title="Visão financeira", icon="📈", default=True)],
        "LANÇAMENTOS": [
            st.Page("app_pages/dfc.py", title="Lançamento", icon="💰"),
            st.Page("app_pages/products.py", title="Produtos", icon="📦"),
        ],
        "ANÁLISES": [st.Page("app_pages/analysis.py", title="Gráficos financeiros", icon="📊")],
        **({
            "DADOS": [
                st.Page("app_pages/import_excel.py", title="Importar planilha", icon="📥"),
                st.Page("app_pages/reset_data.py", title="Reiniciar dados", icon="🧹"),
            ]
        } if can_edit else {}),
    },
    position="sidebar",
)
navigation.run()

st.sidebar.markdown("## 📊 Taqi Motos")
st.sidebar.caption("Painel financeiro")
add_session_controls(role)
if st.sidebar.button(
    "☀️ Tema claro" if dark_mode else "🌙 Tema noturno",
    key="theme_toggle",
    width="stretch",
    help="Alternar entre tema claro e noturno",
):
    st.session_state["app_dark_mode"] = not dark_mode
    st.rerun()
st.sidebar.caption("PostgreSQL na nuvem" if db.engine.dialect.name != "sqlite" else "Demonstração local • SQLite")
