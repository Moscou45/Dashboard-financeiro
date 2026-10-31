import pandas as pd
import streamlit as st

import db
from app_pages.common import MONTHS, brl, selected_year, month_range_filter, period_transactions, export_csv


PAYMENT_ORDER = [
    "Cartão de crédito", "Cartão de débito", "Dinheiro", "Pix", "Transferência",
]
FIXED_CATEGORIES = [
    "COLABORADOR", "ENERGIA", "INTERNET", "PRO-LABORE", "PROGRAMA NEX",
]
VARIABLE_CATEGORIES = [
    "BOLETOS", "COMPRA A VISTA", "FRETE", "IMPOSTO", "LOJA", "OUTROS", "SACOLA",
]


def _money_columns(frame: pd.DataFrame) -> dict:
    return {
        column: st.column_config.NumberColumn(format="R$ %.2f")
        for column in frame.columns
        if column != "Data"
    }


def _expense_section(label: str, expense_type: str, rows: pd.DataFrame, selected_months: list[int], categories: list[str]):
    st.subheader(label)
    with st.form(f"add_{expense_type.casefold()}_expense", clear_on_submit=True):
        a, b = st.columns(2)
        when = a.date_input("Data", value=pd.Timestamp.today().date(), key=f"{expense_type}_date")
        category = b.selectbox("Categoria", categories, index=None, key=f"{expense_type}_category")
        amount = a.number_input("Valor (R$)", min_value=0.01, step=10.0, format="%.2f", key=f"{expense_type}_amount")
        description = b.text_input("Descrição", placeholder="Ex.: fornecedor, detalhe do gasto", key=f"{expense_type}_description")
        submitted = st.form_submit_button(f"Adicionar despesa {expense_type.casefold()}", type="primary", use_container_width=True)
    if submitted:
        if not category.strip():
            st.error("Informe a categoria da despesa.")
        else:
            db.add_transaction(
                when, "Despesa", category, amount,
                expense_type=expense_type, description=description,
            )
            st.success(f"Despesa {expense_type.casefold()} salva na DFC.")
            st.rerun()

    visible = rows[rows["date"].dt.month.isin(selected_months)].copy() if not rows.empty else rows.copy()
    if visible.empty:
        st.caption("Nenhuma despesa deste tipo no período selecionado.")
        return
    visible = visible.rename(columns={
        "date": "Data", "category": "Categoria", "amount": "Valor",
        "description": "Descrição",
    })
    visible["Descrição"] = visible["Descrição"].fillna("")
    visible = visible[["Data", "Categoria", "Valor", "Descrição"]].sort_values("Data", ascending=False)
    st.dataframe(
        visible, hide_index=True, use_container_width=True,
        column_config={
            "Data": st.column_config.DateColumn(format="DD/MM/YYYY"),
            "Valor": st.column_config.NumberColumn(format="R$ %.2f"),
        },
    )
    export_csv(visible, f"Exportar {label} CSV", f"dfc_{expense_type.casefold()}.csv")


def render():
    st.title("DFC")
    st.caption("Cadastre receitas e despesas nesta página. Cada movimentação aparece na seção correspondente.")
    year = selected_year()
    transactions = period_transactions(year)
    data = transactions.copy()
    if not data.empty:
        data["day"] = data["date"].dt.normalize()
        all_days = pd.DatetimeIndex(sorted(data["day"].dropna().unique()), name="Data")
    else:
        all_days = pd.DatetimeIndex([], name="Data")

    daily = pd.DataFrame(index=all_days)
    revenue = data[data["kind"] == "Receita"].copy() if not data.empty else pd.DataFrame()
    if not revenue.empty:
        revenue["payment_method"] = revenue["payment_method"].fillna("Não informada").replace("", "Não informada")
        pivot = revenue.pivot_table(
            index="day", columns="payment_method", values="amount",
            aggfunc="sum", fill_value=0,
        ).reindex(all_days, fill_value=0)
    else:
        pivot = pd.DataFrame(index=all_days)

    for method in PAYMENT_ORDER:
        daily[method] = (
            pd.to_numeric(pivot[method], errors="coerce").fillna(0.0)
            if method in pivot.columns else 0.0
        )
    # Preserve the total of older receipts even when their method is no longer offered.
    daily["Entradas"] = pivot.sum(axis=1).reindex(all_days, fill_value=0.0)
    daily.index.name = "Data"
    daily = daily.reset_index()
    daily["month"] = daily["Data"].dt.month if not daily.empty else pd.Series(dtype="int64")

    filtered_daily = month_range_filter(daily, "dfc_months")
    selected_months = [MONTHS.index(month) + 1 for month in MONTHS
                       if month in st.session_state.get("dfc_months", MONTHS)]

    expense_rows = data[data["kind"] == "Despesa"].copy() if not data.empty else pd.DataFrame(
        columns=["date", "category", "amount", "expense_type", "description"]
    )
    expense_rows["expense_type"] = expense_rows["expense_type"].fillna("").replace("", "Sem classificação")
    fixed = expense_rows[expense_rows["expense_type"].astype(str).str.casefold().str.startswith("fix")].copy()
    variable = expense_rows[expense_rows["expense_type"].astype(str).str.casefold().str.startswith("vari")].copy()
    other = expense_rows[~expense_rows.index.isin(fixed.index) & ~expense_rows.index.isin(variable.index)].copy()

    filtered_expenses = expense_rows[expense_rows["date"].dt.month.isin(selected_months)] if not expense_rows.empty else expense_rows
    in_total = float(filtered_daily["Entradas"].sum()) if not filtered_daily.empty else 0.0
    out_total = float(filtered_expenses["amount"].sum()) if not filtered_expenses.empty else 0.0
    metrics = st.columns(3)
    metrics[0].metric("Entradas no período", brl(in_total))
    metrics[1].metric("Saídas no período", brl(out_total))
    metrics[2].metric("Saldo líquido do período", brl(in_total - out_total))
    st.caption("Saldo líquido = entradas menos saídas. O saldo diário não inclui saldo inicial nem acumula os dias anteriores.")

    receipts = filtered_daily[["Data", *PAYMENT_ORDER, "Entradas"]].copy()
    receipts = receipts[receipts["Entradas"] != 0]
    if receipts.empty:
        receipts = pd.DataFrame(columns=["Data", *PAYMENT_ORDER, "Entradas"])

    with st.container(border=True):
        st.subheader("Receitas")
        with st.form("add_revenue", clear_on_submit=True):
            a, b = st.columns(2)
            when = a.date_input("Data", value=pd.Timestamp.today().date(), key="revenue_date")
            category = b.text_input("Categoria", placeholder="Ex.: vendas, serviços", key="revenue_category")
            amount = a.number_input("Valor (R$)", min_value=0.01, step=10.0, format="%.2f", key="revenue_amount")
            method = b.selectbox("Forma de pagamento", PAYMENT_ORDER, key="revenue_payment_method")
            submitted = st.form_submit_button("Adicionar receita", type="primary", use_container_width=True)
        if submitted:
            if not category.strip():
                st.error("Informe uma categoria para a receita.")
            else:
                db.add_transaction(when, "Receita", category, amount, method)
                st.success("Receita salva na DFC.")
                st.rerun()

        st.dataframe(
            receipts, hide_index=True, use_container_width=True,
            column_config={"Data": st.column_config.DateColumn(format="DD/MM/YYYY"), **_money_columns(receipts)},
        )
        if receipts.empty:
            st.caption("Nenhuma receita no período selecionado. Use o formulário acima para lançar uma receita.")
        export_csv(receipts, "Exportar receitas CSV", f"dfc_receitas_{year}.csv")

    if not other.empty:
        with st.expander("Despesas antigas sem classificação fixa ou variável"):
            visible = other[other["date"].dt.month.isin(selected_months)].copy()
            if not visible.empty:
                visible = visible.rename(columns={"date": "Data", "category": "Categoria", "amount": "Valor", "description": "Descrição"})
                visible["Descrição"] = visible["Descrição"].fillna("")
                visible = visible[["Data", "Categoria", "Valor", "Descrição"]].sort_values("Data", ascending=False)
                st.dataframe(visible, hide_index=True, use_container_width=True, column_config={
                    "Data": st.column_config.DateColumn(format="DD/MM/YYYY"),
                    "Valor": st.column_config.NumberColumn(format="R$ %.2f"),
                })
            else:
                st.caption("Nenhuma despesa sem classificação neste período.")

    _expense_section("Despesas fixas", "Fixa", fixed, selected_months, FIXED_CATEGORIES)
    _expense_section("Despesas variáveis", "Variável", variable, selected_months, VARIABLE_CATEGORIES)

    daily_summary = pd.DataFrame(index=all_days)
    daily_summary["Entradas"] = daily["Entradas"].to_numpy() if not daily.empty else []
    daily_summary["Saídas"] = 0.0
    if not expense_rows.empty:
        expense_by_day = expense_rows.assign(day=expense_rows["date"].dt.normalize()).groupby("day")["amount"].sum()
        daily_summary["Saídas"] = expense_by_day.reindex(all_days, fill_value=0.0)
    daily_summary["Saldo do dia"] = daily_summary["Entradas"] - daily_summary["Saídas"]
    daily_summary.index.name = "Data"
    daily_summary = daily_summary.reset_index()
    daily_summary["month"] = daily_summary["Data"].dt.month
    selected_daily = daily_summary[daily_summary["month"].isin(selected_months)]
    if not selected_daily.empty:
        with st.expander("Resumo diário de entradas, saídas e saldo"):
            visible = selected_daily.drop(columns=["month"])
            st.dataframe(visible, hide_index=True, use_container_width=True, column_config={
                "Data": st.column_config.DateColumn(format="DD/MM/YYYY"),
                **_money_columns(visible),
            })
            export_csv(visible, "Exportar resumo diário CSV", f"dfc_resumo_diario_{year}.csv")


render()
