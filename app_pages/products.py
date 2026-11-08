import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import db
from charts import CHART_CONFIG
from app_pages.common import MONTHS, selected_year


MONTH_NAMES = [
    "JANEIRO", "FEVEREIRO", "MARÇO", "ABRIL", "MAIO", "JUNHO",
    "JULHO", "AGOSTO", "SETEMBRO", "OUTUBRO", "NOVEMBRO", "DEZEMBRO",
]
NAVY = "#06265d"
BAR_BLUE = "#4188f2"


def _brl(value: float) -> str:
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _money_chart(labels: list[str], values: list[float], title: str, key: str, alt: str):
    return _ranking_chart(labels, values, title, key, alt, "money")


def _ranking_chart(labels: list[str], values: list[float], title: str, key: str, alt: str, value_kind: str):
    if value_kind == "money":
        text = [_brl(value) for value in values]
        hover = "R$ %{x:,.2f}"
    elif value_kind == "percent":
        text = [f"{value:.2f}%".replace(".", ",") for value in values]
        hover = "%{x:.2f}%"
    else:
        text = [f"{value:,.0f}".replace(",", ".") for value in values]
        hover = "%{x:,.0f} unidades"

    fig = go.Figure(go.Bar(
        x=values,
        y=labels,
        orientation="h",
        marker={"color": BAR_BLUE, "line": {"color": "#78aaff", "width": 1}},
        text=text,
        textposition="outside",
        textfont={"color": "white", "size": 10},
        cliponaxis=False,
        hovertemplate=f"<b>%{{y}}</b><br>{hover}<extra></extra>",
    ))
    max_value = max(values, default=0.0)
    fig.update_layout(
        title={"text": title, "x": 0.5, "xanchor": "center", "font": {"size": 15, "color": "white"}},
        paper_bgcolor=NAVY,
        plot_bgcolor=NAVY,
        font={"family": "Inter, Arial, sans-serif", "size": 9, "color": "white"},
        height=max(330, 27 * len(labels) + 100),
        margin={"l": 245, "r": 92, "t": 48, "b": 24},
        showlegend=False,
        bargap=0.3,
        hoverlabel={"bgcolor": "#172033", "font": {"color": "white"}},
    )
    fig.update_xaxes(
        visible=False,
        showgrid=False,
        zeroline=False,
        range=[0, max_value * 1.24 if max_value > 0 else 1],
    )
    fig.update_yaxes(
        autorange="reversed",
        showgrid=False,
        zeroline=False,
        tickfont={"size": 9, "color": "white"},
    )
    return fig


def _show_chart(fig, alt: str, key: str):
    st.plotly_chart(fig, width="stretch", theme=None, config=CHART_CONFIG, alt=alt, key=key)


def render():
    st.title("Produtos")
    year = selected_year()
    products = db.get_products(year)

    available = set(products["month_num"].dropna().astype(int).tolist()) if not products.empty else set()
    first_month = min(available) if available else 1
    month_label = st.selectbox(
        "Mês",
        ["Todos os meses", *MONTH_NAMES],
        index=first_month,
        format_func=lambda value: value.title() if value != "Todos os meses" else value,
        key="product_month_filter",
    )
    if month_label == "Todos os meses":
        view = products.copy()
    else:
        month_num = MONTH_NAMES.index(month_label) + 1
        view = products[products["month_num"] == month_num].copy() if not products.empty else products.copy()

    if view.empty:
        st.info(f"Não há produtos cadastrados em {month_label.title()} de {year}.")
        return

    agg = view.groupby("product", as_index=False).agg(
        quantity=("quantity", "sum"),
        revenue=("revenue", "sum"),
        cost=("cost", "sum"),
        profit=("profit", "sum"),
    )
    agg["profit_percent"] = agg["profit"].div(agg["revenue"].where(agg["revenue"].ne(0))).mul(100).fillna(0)

    by_revenue = agg.sort_values("revenue", ascending=False).head(10)
    by_profit = agg.sort_values("profit", ascending=False).head(10)
    by_margin = agg.sort_values("profit_percent", ascending=False).head(10)
    by_quantity = agg.sort_values("quantity", ascending=False).head(10)

    top_left, top_right = st.columns(2)
    with top_left:
        _show_chart(
            _money_chart(by_revenue["product"].tolist(), by_revenue["revenue"].astype(float).tolist(),
                         "PRODUTOS MAIS VENDIDOS", "product_revenue", "Ranking de produtos por receita total"),
            "Ranking dos dez produtos com maior receita",
            "product_revenue",
        )
    with top_right:
        _show_chart(
            _money_chart(by_profit["product"].tolist(), by_profit["profit"].astype(float).tolist(),
                         "PRODUTOS/LUCRO R$", "product_profit", "Ranking de produtos por lucro em reais"),
            "Ranking dos dez produtos com maior lucro em reais",
            "product_profit",
        )

    bottom_left, bottom_right = st.columns(2)
    with bottom_left:
        _show_chart(
            _ranking_chart(by_margin["product"].tolist(), by_margin["profit_percent"].astype(float).tolist(),
                           "PRODUTOS/LUCRO %", "product_margin", "Ranking de margem por produto", "percent"),
            "Ranking dos dez produtos por lucro percentual",
            "product_margin",
        )
    with bottom_right:
        _show_chart(
            _ranking_chart(by_quantity["product"].tolist(), by_quantity["quantity"].astype(float).tolist(),
                           "PRODUTOS/QUANTIDADE", "product_quantity", "Ranking de produtos por quantidade", "quantity"),
            "Ranking dos dez produtos com maior quantidade vendida",
            "product_quantity",
        )


render()
