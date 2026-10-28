import numpy as np
import pandas as pd
import streamlit as st

import db
from charts import CHART_CONFIG, donut_chart, financial_overview, grouped_bar, payment_chart, variation_chart
from app_pages.common import MONTHS, brl, selected_year, month_range_filter, export_csv, warning_reconciliation, period_transactions


def _show_chart(figure, alt: str, key: str):
    st.plotly_chart(figure, width="stretch", theme=None, config=CHART_CONFIG, alt=alt, key=key)


def render():
    st.title("Visão financeira")
    st.caption("Receitas, despesas, saldo e formas de pagamento — valores em reais.")
    year = selected_year()
    monthly = db.get_monthly_summary(year)
    monthly["month_label"] = [MONTHS[m - 1] for m in monthly.month]

    # Compare each month with the previous calendar month, then apply the view filter.
    for source, target in (("revenue", "revenue_change"), ("expenses", "expense_change")):
        previous = monthly[source].shift(1)
        change = (monthly[source].div(previous).sub(1).mul(100)).where(previous.ne(0))
        monthly[target] = change.replace([np.inf, -np.inf], np.nan)

    filtered = month_range_filter(monthly, "dashboard_months")
    if filtered.empty:
        st.info("Selecione ao menos um mês para visualizar os indicadores.")
        return

    totals = filtered[["revenue", "expenses", "balance"]].sum()
    cols = st.columns(3)
    cols[0].metric("Receitas no período", brl(totals.revenue))
    cols[1].metric("Despesas no período", brl(totals.expenses))
    cols[2].metric("Saldo do período", brl(totals.balance), delta="Negativo" if totals.balance < 0 else "Positivo", delta_color="inverse" if totals.balance < 0 else "normal")

    _show_chart(
        financial_overview(filtered.month_label, filtered.revenue, filtered.expenses, filtered.balance),
        "Gráfico interativo de receitas, despesas e saldo mensal",
        "financial_overview",
    )

    transactions = period_transactions(year)
    warning_reconciliation(year, transactions)
    transactions = transactions[transactions.date.dt.month.isin(filtered.month)]
    expenses = transactions[transactions.kind == "Despesa"].copy()
    expenses["expense_type"] = expenses.expense_type.fillna("Não classificada").replace("", "Não classificada")

    fixed_expenses = expenses[expenses.expense_type.str.casefold() == "fixa"].groupby("category").amount.sum().sort_values(ascending=False)
    variable_expenses = expenses[expenses.expense_type.str.casefold() == "variável"].groupby("category").amount.sum().sort_values(ascending=False)
    left, right = st.columns(2)
    with left:
        _show_chart(donut_chart(fixed_expenses.index, fixed_expenses.values, "Despesas fixas por categoria"), "Gráfico de rosca das despesas fixas por categoria", "fixed_expenses")
    with right:
        _show_chart(donut_chart(variable_expenses.index, variable_expenses.values, "Despesas variáveis por categoria"), "Gráfico de rosca das despesas variáveis por categoria", "variable_expenses")

    grouped = expenses.groupby([expenses.date.dt.month, expenses.expense_type.str.casefold()]).amount.sum().unstack(fill_value=0)
    fixed = [float(grouped.loc[m, "fixa"]) if m in grouped.index and "fixa" in grouped else 0 for m in filtered.month]
    variable = [float(grouped.loc[m, "variável"]) if m in grouped.index and "variável" in grouped else 0 for m in filtered.month]
    _show_chart(
        grouped_bar(filtered.month_label, [fixed, variable], "Despesas fixas e variáveis por mês", ["Fixa", "Variável"], ["#8b6fe8", "#f1a33c"]),
        "Comparação mensal de despesas fixas e variáveis",
        "fixed_vs_variable",
    )

    _show_chart(
        variation_chart(filtered.month_label, filtered.revenue_change, filtered.expense_change),
        "Variação percentual mensal de receitas e despesas em relação ao mês anterior",
        "monthly_variation",
    )

    pay = transactions[transactions.payment_method.notna() & (transactions.payment_method != "")].copy()
    if pay.empty:
        st.info("Não há formas de pagamento classificadas nos lançamentos selecionados.")
    else:
        pay_table = pay.pivot_table(index=pay.date.dt.month, columns="payment_method", values="amount", aggfunc="sum", fill_value=0).reindex(filtered.month, fill_value=0)
        _show_chart(
            payment_chart(filtered.month_label, [pay_table[column].tolist() for column in pay_table.columns], list(pay_table.columns)),
            "Valores mensais por forma de pagamento",
            "payment_methods",
        )

    with st.expander("Entenda os dados desta página"):
        st.write("Os totais mensais de receita e despesa preservam o resumo consolidado da aba MES. As aberturas por categoria, tipo de despesa e forma de pagamento vêm dos lançamentos da DFC. A planilha apresenta diferenças entre essas fontes em alguns meses; por isso o app mostra o aviso de conciliação sem ajustar valores automaticamente.")
    export = filtered[["month_label", "revenue", "expenses", "balance"]].rename(columns={"month_label": "Mês", "revenue": "Receitas", "expenses": "Despesas", "balance": "Saldo"})
    export_csv(export, "Exportar resumo CSV", f"resumo_financeiro_{year}.csv")


render()

