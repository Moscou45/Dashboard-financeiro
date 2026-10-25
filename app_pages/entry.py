from datetime import date
import streamlit as st

import db
from auth import require_editor


def render():
    require_editor()
    st.title("Cadastro de movimenta��es")
    st.caption("Os lan�amentos salvos aparecem imediatamente nos indicadores do prot�tipo.")
    tab_fin, tab_prod = st.tabs(["Movimenta��o financeira", "Venda de produto"])
    with tab_fin:
        with st.form("financial_entry", clear_on_submit=True):
            a, b = st.columns(2)
            when = a.date_input("Data", value=date.today())
            kind = b.selectbox("Tipo", ["Receita", "Despesa"])
            category = a.text_input("Categoria", placeholder="Ex.: Venda, aluguel, pe�as")
            amount = b.number_input("Valor (R$)", min_value=0.01, step=10.0, format="%.2f")
            method = a.selectbox("Forma de pagamento", ["N�o informada", "Dinheiro", "Pix", "Cart�o de d�bito", "Cart�o de cr�dito", "Boleto", "Transfer�ncia", "Outro"])
            expense_type = b.selectbox("Classifica��o da despesa", ["N�o se aplica", "Fixa", "Vari�vel", "N�o classificada"])
            submitted = st.form_submit_button("Salvar movimenta��o", type="primary", use_container_width=True)
        if submitted:
            if not category.strip():
                st.error("Informe uma categoria para salvar.")
            else:
                db.add_transaction(when, kind, category, amount, None if method == "N�o informada" else method,
                                   None if expense_type == "N�o se aplica" else expense_type)
                st.success("Movimenta��o salva.")
                st.rerun()
    with tab_prod:
        with st.form("product_entry", clear_on_submit=True):
            a, b = st.columns(2)
            when = a.date_input("Data da venda", value=date.today(), key="product_date")
            product = b.text_input("Produto")
            quantity = a.number_input("Quantidade", min_value=0.01, step=1.0)
            cost = b.number_input("Custo total (R$)", min_value=0.0, step=10.0)
            revenue = a.number_input("Receita total (R$)", min_value=0.0, step=10.0)
            submitted = st.form_submit_button("Salvar venda", type="primary", use_container_width=True)
        if submitted:
            if not product.strip():
                st.error("Informe o nome do produto.")
            else:
                import calendar
                db.add_product(when.year, when.month, calendar.month_name[when.month], product, quantity, cost, revenue)
                st.success("Venda de produto salva.")
                st.rerun()


render()
