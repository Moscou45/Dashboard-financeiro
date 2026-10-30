from datetime import date
import streamlit as st

import db
from auth import require_editor


def render():
    require_editor()
    st.title("Cadastrar dados")
    st.caption("Cadastre cada movimentação uma vez. Receitas e despesas aparecem automaticamente na DFC e nos gráficos.")
    tab_fin, tab_prod = st.tabs(["Movimentação financeira", "Venda de produto"])
    with tab_fin:
        with st.form("financial_entry", clear_on_submit=True):
            a, b = st.columns(2)
            when = a.date_input("Data", value=date.today())
            kind = b.selectbox("Tipo", ["Receita", "Despesa"])
            category = a.text_input("Categoria", placeholder="Ex.: venda, aluguel, peças")
            amount = b.number_input("Valor (R$)", min_value=0.01, step=10.0, format="%.2f")
            method = a.selectbox("Forma de pagamento", ["Selecione", "Dinheiro", "Pix", "Cartão de débito", "Cartão de crédito", "Transferência", "Boleto", "Outro"])
            expense_type = b.selectbox("Classificação da despesa", ["Não se aplica", "Fixa", "Variável"])
            submitted = st.form_submit_button("Salvar movimentação", type="primary", use_container_width=True)
        if submitted:
            if not category.strip():
                st.error("Informe uma categoria para salvar.")
            elif method == "Selecione":
                st.error("Selecione a forma de pagamento.")
            elif kind == "Despesa" and expense_type not in ("Fixa", "Variável"):
                st.error("Classifique a despesa como fixa ou variável.")
            else:
                db.add_transaction(
                    when, kind, category, amount, method,
                    None if kind == "Receita" else expense_type,
                )
                st.success("Movimentação salva e refletida na DFC.")
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
