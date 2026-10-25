import streamlit as st
import pandas as pd

import db
from charts import bars3d
from app_pages.common import brl, selected_year, export_csv


def render():
    st.title("Produtos")
    st.caption("Produtos vendidos, quantidade, receita e lucro registrado na base importada.")
    year = selected_year()
    products = db.get_products(year)
    if products.empty:
        st.info("Ainda não há vendas de produtos cadastradas para este ano.")
        return
    months = sorted(products.month_num.dropna().astype(int).unique().tolist())
    month_labels = {int(r.month_num): r.month_label.title() for r in products.itertuples() if pd.notna(r.month_num)}
    options = [month_labels.get(m, str(m)) for m in months]
    selected = st.multiselect("Meses", options, default=options, key="product_months")
    chosen_months = [months[options.index(x)] for x in selected]
    view = products[products.month_num.isin(chosen_months)] if chosen_months else products.iloc[0:0]
    if view.empty:
        st.info("Selecione ao menos um mês com vendas de produtos.")
        return
    agg = view.groupby("product", as_index=False).agg(quantity=("quantity", "sum"), revenue=("revenue", "sum"), cost=("cost", "sum"), profit=("profit", "sum"))
    by_qty = agg.sort_values("quantity", ascending=False).head(12)
    by_profit = agg.sort_values("profit", ascending=False).head(12)
    c = st.columns(3)
    c[0].metric("Unidades vendidas", f"{view.quantity.sum():,.0f}".replace(",", "."))
    c[1].metric("Receita de produtos", brl(view.revenue.sum()))
    c[2].metric("Lucro registrado", brl(view.profit.sum()))
    st.pyplot(bars3d(by_qty.product, [by_qty.quantity], "Mais vendidos por quantidade", ["Unidades"], ["#526bff"], currency=False), width="stretch", alt="Gráfico 3D com os doze produtos mais vendidos por quantidade")
    st.pyplot(bars3d(by_profit.product, [by_profit.profit], "Produtos com maior lucro registrado", ["Lucro"], ["#29b6a6"]), width="stretch", alt="Gráfico 3D com os doze produtos com maior lucro")
    st.subheader("Detalhamento por produto")
    table = agg.sort_values("profit", ascending=False).rename(columns={"product":"Produto", "quantity":"Quantidade", "revenue":"Receita", "cost":"Custo", "profit":"Lucro"})
    st.dataframe(table, hide_index=True, use_container_width=True, column_config={"Receita":st.column_config.NumberColumn(format="R$ %.2f"), "Custo":st.column_config.NumberColumn(format="R$ %.2f"), "Lucro":st.column_config.NumberColumn(format="R$ %.2f")})
    export_csv(table, "Exportar produtos CSV", f"produtos_{year}.csv")
    st.caption("O lucro por produto é calculado como receita menos custo na própria linha. Margem e lucro líquido consolidado permanecem fora desta versão.")


render()
