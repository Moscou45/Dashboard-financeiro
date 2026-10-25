import calendar
import numpy as np
import pandas as pd
import streamlit as st

import db
from charts import bars3d, pie3d, line_chart
from app_pages.common import MONTHS, brl, selected_year, month_range_filter, export_csv, warning_reconciliation, period_transactions


def render():
    st.title("Visão financeira")
    st.caption("Receitas, despesas, saldo e formas de pagamento — valores em reais.")
    year = selected_year()
    monthly = db.get_monthly_summary(year)
    monthly["month_label"] = [MONTHS[m-1] for m in monthly.month]
    # Compute each calendar month's change before applying the display filter.
    monthly["revenue_change"] = monthly.revenue.pct_change() * 100
    monthly["expense_change"] = monthly.expenses.pct_change() * 100
    filtered = month_range_filter(monthly, "dashboard_months")
    if filtered.empty:
        st.info("Selecione ao menos um mês para visualizar os indicadores.")
        return
    totals = filtered[["revenue", "expenses", "balance"]].sum()
    cols = st.columns(3)
    cols[0].metric("Receitas no período", brl(totals.revenue))
    cols[1].metric("Despesas no período", brl(totals.expenses))
    cols[2].metric("Saldo do período", brl(totals.balance), delta="Negativo" if totals.balance < 0 else "Positivo", delta_color="inverse" if totals.balance < 0 else "normal")
    st.pyplot(bars3d(filtered.month_label, [filtered.revenue, filtered.expenses, filtered.balance], "Receitas, despesas e saldo mensal", ["Receita", "Despesa", "Saldo"], ["#526bff", "#ef6a72", "#29b6a6"]), width="stretch", alt="Gráfico 3D de colunas mensais de receitas, despesas e saldo")

    transactions = period_transactions(year)
    warning_reconciliation(year, transactions)
    transactions = transactions[transactions.date.dt.month.isin(filtered.month)]
    expenses = transactions[transactions.kind == "Despesa"].copy()
    expenses["expense_type"] = expenses.expense_type.fillna("Não classificada").replace("", "Não classificada")
    a, b = st.columns(2)
    for col, typ, title in [(a, "Fixa", "Despesas fixas"), (b, "Variável", "Despesas variáveis")]:
        sub = expenses[expenses.expense_type.str.casefold() == typ.casefold()].groupby("category").amount.sum().sort_values(ascending=False)
        with col:
            st.pyplot(pie3d(sub.index.tolist(), sub.values, title), width="stretch", alt=f"Gráfico de pizza 3D de {title.lower()} por categoria")
    grouped = expenses.groupby([expenses.date.dt.month, "expense_type"]).amount.sum().unstack(fill_value=0)
    fixed = [float(grouped.loc[m, "Fixa"]) if m in grouped.index and "Fixa" in grouped else 0 for m in filtered.month]
    variable = [float(grouped.loc[m, "Variável"]) if m in grouped.index and "Variável" in grouped else 0 for m in filtered.month]
    st.pyplot(bars3d(filtered.month_label, [fixed, variable], "Despesas fixas x variáveis", ["Fixa", "Variável"], ["#9270db", "#f5b544"]), width="stretch", alt="Comparação mensal em colunas 3D entre despesas fixas e variáveis")

    st.pyplot(bars3d(filtered.month_label, [filtered.revenue_change.fillna(0), filtered.expense_change.fillna(0)], "Variação mensal de receitas e despesas (%)", ["Receita %", "Despesa %"], ["#526bff", "#ef6a72"], currency=False), width="stretch", alt="Variação percentual mês a mês de receitas e despesas")

    pay = transactions[transactions.payment_method.notna() & (transactions.payment_method != "")].copy()
    if pay.empty:
        st.info("Não há formas de pagamento classificadas nos lançamentos selecionados.")
    else:
        pay_table = pay.pivot_table(index=pay.date.dt.month, columns="payment_method", values="amount", aggfunc="sum", fill_value=0).reindex(filtered.month, fill_value=0)
        st.pyplot(bars3d(filtered.month_label, [pay_table[c].tolist() for c in pay_table.columns], "Movimentações por forma de pagamento", list(pay_table.columns)), width="stretch", alt="Valores por mês e forma de pagamento em colunas 3D")
    with st.expander("Entenda os dados desta página"):
        st.write("Os totais mensais de receita e despesa preservam o resumo consolidado da aba MES. As aberturas por categoria, tipo de despesa e forma de pagamento vêm dos lançamentos da DFC. A planilha apresenta diferenças entre essas fontes em alguns meses; por isso o app mostra o aviso de conciliação sem ajustar valores automaticamente.")
    export = filtered[["month_label", "revenue", "expenses", "balance"]].rename(columns={"month_label":"Mês", "revenue":"Receitas", "expenses":"Despesas", "balance":"Saldo"})
    export_csv(export, "Exportar resumo CSV", f"resumo_financeiro_{year}.csv")


render()
