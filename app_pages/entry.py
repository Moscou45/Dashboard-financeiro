from datetime import date
import calendar
import streamlit as st

import db
from auth import require_editor


def render():
    require_editor()
    st.title("Cadastrar produtos")
    st.caption("Registre as vendas de produtos para acompanhar quantidade, custo, receita e lucro.")
    with st.form("product_entry", clear_on_submit=True):
        a, b = st.columns(2)
        when = a.date_input("Data da venda", value=date.today())
        product = b.text_input("Produto")
        quantity = a.number_input("Quantidade", min_value=0.01, step=1.0)
        cost = b.number_input("Custo total (R$)", min_value=0.0, step=10.0)
        revenue = a.number_input("Receita total (R$)", min_value=0.0, step=10.0)
        submitted = st.form_submit_button("Salvar venda", type="primary", use_container_width=True)
    if submitted:
        if not product.strip():
            st.error("Informe o nome do produto.")
        else:
            db.add_product(when.year, when.month, calendar.month_name[when.month], product, quantity, cost, revenue)
            st.success("Venda de produto salva.")
            st.rerun()


render()
