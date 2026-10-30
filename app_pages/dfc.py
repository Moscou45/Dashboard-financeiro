import pandas as pd
import streamlit as st

import db
from app_pages.common import MONTHS, brl, selected_year, month_range_filter, period_transactions, export_csv


PAYMENT_ORDER = [
    "Dinheiro", "Pix", "Cartão de débito", "Cartão de crédito",
    "Transferência", "Boleto", "Outro", "Não informada",
]


def _series_or_zero(frame: pd.DataFrame, column: str, dates: pd.DatetimeIndex) -> pd.Series:
    if column not in frame.columns:
        return pd.Series(0.0, index=dates)
    return pd.to_numeric(frame[column], errors="coerce").reindex(dates, fill_value=0.0).fillna(0.0)


def render():
    st.title("DFC")
    st.caption("Resumo diário das entradas por forma de pagamento e das saídas por classificação.")
    year = selected_year()
    transactions = period_transactions(year)
    if transactions.empty:
        st.info("Ainda não há movimentações. Cadastre receitas e despesas para preencher a DFC.")
        return

    data = transactions.copy()
    data["day"] = data["date"].dt.normalize()
    all_days = pd.DatetimeIndex(sorted(data["day"].dropna().unique()), name="Data")

    revenue = data[data["kind"] == "Receita"].copy()
    revenue["payment_method"] = revenue["payment_method"].fillna("Não informada").replace("", "Não informada")
    if revenue.empty:
        by_payment = pd.DataFrame(index=all_days)
    else:
        by_payment = revenue.pivot_table(
            index="day", columns="payment_method", values="amount",
            aggfunc="sum", fill_value=0,
        ).reindex(all_days, fill_value=0)

    expense = data[data["kind"] == "Despesa"].copy()
    expense["expense_type"] = expense["expense_type"].fillna("Não classificada").replace("", "Não classificada")
    if expense.empty:
        by_expense_type = pd.DataFrame(index=all_days)
        expense_total = pd.Series(0.0, index=all_days)
    else:
        by_expense_type = expense.pivot_table(
            index="day", columns="expense_type", values="amount",
            aggfunc="sum", fill_value=0,
        ).reindex(all_days, fill_value=0)
        expense_total = expense.groupby("day")["amount"].sum().reindex(all_days, fill_value=0.0)

    fixed = _series_or_zero(by_expense_type, "Fixa", all_days)
    variable = _series_or_zero(by_expense_type, "Variável", all_days)
    other_expense = expense_total - fixed - variable

    payment_methods = [name for name in PAYMENT_ORDER if name in by_payment.columns]
    payment_methods.extend(sorted(str(name) for name in by_payment.columns if name not in payment_methods))
    daily = pd.DataFrame(index=all_days)
    for method in payment_methods:
        daily[method] = _series_or_zero(by_payment, method, all_days)
    daily["Entradas"] = daily[payment_methods].sum(axis=1) if payment_methods else 0.0
    daily["Despesas fixas"] = fixed
    daily["Despesas variáveis"] = variable
    daily["Outras despesas"] = other_expense
    daily["Saídas"] = expense_total
    daily["Saldo do dia"] = daily["Entradas"] - daily["Saídas"]
    daily.index.name = "Data"
    daily = daily.reset_index()
    daily["month"] = daily["Data"].dt.month

    filtered = month_range_filter(daily, "dfc_months")
    if filtered.empty:
        st.info("Selecione ao menos um mês para ver a DFC.")
        return

    totals = filtered[["Entradas", "Saídas", "Saldo do dia"]].sum()
    cols = st.columns(3)
    cols[0].metric("Entradas no período", brl(totals["Entradas"]))
    cols[1].metric("Saídas no período", brl(totals["Saídas"]))
    cols[2].metric("Saldo líquido do período", brl(totals["Saldo do dia"]))
    st.caption("Saldo do dia = entradas do dia menos saídas do dia. Ele não inclui saldo inicial nem acumula os dias anteriores.")

    visible = filtered.drop(columns=["month"]).copy()
    money_columns = [column for column in visible.columns if column != "Data"]
    config = {column: st.column_config.NumberColumn(format="R$ %.2f") for column in money_columns}
    st.dataframe(visible, hide_index=True, use_container_width=True, column_config=config)
    export_csv(visible, "Exportar DFC CSV", "dfc_" + str(year) + ".csv")

    with st.expander("Lançamentos que compõem a DFC"):
        details = transactions[transactions["date"].dt.month.isin(filtered["month"])].copy()
        details = details[["date", "kind", "category", "expense_type", "payment_method", "amount"]]
        details = details.rename(columns={
            "date": "Data", "kind": "Tipo", "category": "Categoria",
            "expense_type": "Classificação", "payment_method": "Forma de pagamento",
            "amount": "Valor",
        })
        st.dataframe(details, hide_index=True, use_container_width=True, column_config={"Valor": st.column_config.NumberColumn(format="R$ %.2f")})


render()
