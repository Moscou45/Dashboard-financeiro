from __future__ import annotations

import calendar
import pandas as pd
import streamlit as st
import db

MONTHS = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]


def brl(value: float) -> str:
    return f"R$ {float(value):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def selected_year() -> int:
    df = db.get_transactions()
    years = sorted(set(df["date"].dt.year.dropna().astype(int))) if not df.empty else []
    products = db.get_products(2026)
    if not products.empty:
        years = sorted(set(years) | set(products.year.astype(int)))
    if 2026 not in years:
        years.append(2026)
    return int(st.sidebar.selectbox("Ano", sorted(years, reverse=True)))


def month_range_filter(df: pd.DataFrame, key: str) -> pd.DataFrame:
    months = st.sidebar.multiselect("Meses", MONTHS, default=MONTHS, key=key)
    chosen = [MONTHS.index(m) + 1 for m in months]
    return df[df["month"].isin(chosen)].copy()


def export_csv(df: pd.DataFrame, label: str, filename: str):
    data = df.to_csv(index=False, sep=";", decimal=",").encode("utf-8-sig")
    st.download_button(label, data, filename, "text/csv", use_container_width=True)


def warning_reconciliation(year: int, transactions: pd.DataFrame):
    if transactions.empty:
        return
    details = transactions[transactions.kind == "Despesa"].copy()
    details["month"] = details.date.dt.month
    detail_month = details.groupby("month").amount.sum()
    summary = db.get_monthly_summary(year).set_index("month")
    diffs = []
    for month, detail_total in detail_month.items():
        consolidated = float(summary.loc[month, "expenses"])
        delta = float(detail_total - consolidated)
        if abs(delta) > .02:
            diffs.append(f"{MONTHS[month-1]}: {brl(delta)}")
    if diffs:
        st.warning("A soma dos lançamentos categorizados de despesas não coincide com o total consolidado da aba MES em alguns meses (" + "; ".join(diffs[:5]) + "). Os gráficos mensais usam o resumo consolidado; os gráficos por categoria/pagamento usam os lançamentos detalhados da DFC.")


def period_transactions(year: int) -> pd.DataFrame:
    df = db.get_transactions()
    if df.empty:
        return df
    return df[df.date.dt.year == year].copy()
