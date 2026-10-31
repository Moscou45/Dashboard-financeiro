from calendar import monthrange
import pandas as pd
import streamlit as st

import db
from app_pages.common import MONTHS, brl, selected_year, period_transactions, export_csv, warning_reconciliation
from charts import CHART_CONFIG, grouped_bar, pie_chart, expense_variation_chart


FIXED_ORDER = ["COLABORADOR", "PRO-LABORE", "ENERGIA", "INTERNET", "PROGRAMA NEX"]
VARIABLE_ORDER = ["COMPRA A VISTA", "BOLETOS", "OUTROS", "SACOLA", "FRETE", "LOJA", "IMPOSTO"]
MONTH_COLORS = [
    "#3978c5", "#d84a4a", "#f2b632", "#45a95b", "#f08032", "#36a7ad",
    "#245bb5", "#b5372e", "#8c7822", "#2f7547", "#9a5b2d", "#367d80",
]


def _percent(value: float, denominator: float) -> str:
    if denominator <= 0:
        return "—"
    pct = 100 * float(value) / float(denominator)
    return f"{pct:,.2f}%".replace(",", "X").replace(".", ",").replace("X", ".")


def _show_chart(figure, alt: str, key: str):
    st.plotly_chart(figure, width="stretch", theme=None, config=CHART_CONFIG, alt=alt, key=key)


def _expense_rows(transactions: pd.DataFrame) -> pd.DataFrame:
    if transactions.empty:
        return pd.DataFrame(columns=["date", "kind", "category", "amount", "expense_type", "category_key", "month"])
    rows = transactions[transactions["kind"] == "Despesa"].copy()
    if rows.empty:
        return pd.DataFrame(columns=["date", "kind", "category", "amount", "expense_type", "category_key", "month"])
    rows["category_key"] = rows["category"].fillna("Sem categoria").astype(str).str.strip().str.upper()
    rows["expense_type"] = rows["expense_type"].fillna("").astype(str).str.strip()
    rows["month"] = rows["date"].dt.month
    return rows


def _comparison_chart(expenses: pd.DataFrame, expense_type: str, base_categories: list[str], title: str, key: str):
    subset = expenses[expenses["expense_type"].str.casefold() == expense_type.casefold()].copy()
    present = set(subset["category_key"].unique()) if not subset.empty else set()
    categories = [name for name in base_categories if name in present or not present]
    categories.extend(sorted(present - set(categories)))
    if not categories:
        categories = base_categories.copy()

    filter_col, chart_col = st.columns([1, 4])
    with filter_col:
        selected = st.selectbox(
            "Categoria", ["Todas", *categories], key=f"{key}_category_filter"
        )
    visible_categories = categories if selected == "Todas" else [selected]
    if subset.empty:
        pivot = pd.DataFrame(0.0, index=categories, columns=range(1, 13))
    else:
        pivot = subset.pivot_table(
            index="category_key", columns="month", values="amount",
            aggfunc="sum", fill_value=0.0,
        ).reindex(index=categories, columns=range(1, 13), fill_value=0.0)
    series = [
        [float(pivot.loc[category, month]) for category in visible_categories]
        for month in range(1, 13)
    ]
    with chart_col:
        _show_chart(
            grouped_bar(
                visible_categories, series, title, MONTHS, MONTH_COLORS,
                currency=True, horizontal=False,
            ),
            f"Comparação mensal de {expense_type.casefold()} por categoria",
            key,
        )


def _variation_chart(expenses: pd.DataFrame, expense_type: str, base_categories: list[str], key: str):
    subset = expenses[expenses["expense_type"].str.casefold() == expense_type.casefold()].copy()
    present = set(subset["category_key"].unique()) if not subset.empty else set()
    categories = [name for name in base_categories if name in present or not present]
    categories.extend(sorted(present - set(categories)))
    if not categories:
        categories = base_categories.copy()

    filter_col, chart_col = st.columns([1, 4])
    with filter_col:
        category = st.selectbox(
            "Categoria", categories, key=f"{key}_category_filter"
        )
    category_rows = subset[subset["category_key"] == category]
    monthly_totals = (
        category_rows.groupby("month")["amount"].sum().reindex(range(1, 13), fill_value=0.0)
        if not category_rows.empty else pd.Series(0.0, index=range(1, 13))
    )
    changes: list[float | None] = [None]
    for month in range(2, 13):
        previous = float(monthly_totals.loc[month - 1])
        current = float(monthly_totals.loc[month])
        changes.append((current / previous - 1) * 100 if previous > 0 else None)
    with chart_col:
        _show_chart(
            expense_variation_chart(
                MONTHS, changes,
                f"Variação mensal de {category.title()}",
            ),
            f"Variação percentual mensal da despesa {category.title()}",
            key,
        )


def _monthly_expense_table(month: int, revenue: float, expenses: pd.DataFrame, categories: list[str]) -> pd.DataFrame:
    month_rows = expenses[expenses["month"] == month] if not expenses.empty else expenses
    totals = month_rows.groupby("category_key")["amount"].sum().to_dict() if not month_rows.empty else {}
    fixed_total = float(month_rows.loc[month_rows["expense_type"].str.casefold() == "fixa", "amount"].sum()) if not month_rows.empty else 0.0
    variable_total = float(month_rows.loc[month_rows["expense_type"].str.casefold() == "variável", "amount"].sum()) if not month_rows.empty else 0.0
    rows = [
        {"Descrição": category.title(), "Valor": float(totals.get(category, 0.0)),
         "% do faturamento": _percent(float(totals.get(category, 0.0)), revenue)}
        for category in categories
    ]
    rows.extend([
        {"Descrição": "Despesas variáveis", "Valor": variable_total,
         "% do faturamento": _percent(variable_total, revenue)},
        {"Descrição": "Despesas fixas", "Valor": fixed_total,
         "% do faturamento": _percent(fixed_total, revenue)},
        {"Descrição": "Faturamento", "Valor": revenue,
         "% do faturamento": _percent(revenue, revenue)},
    ])
    return pd.DataFrame(rows)


def render():
    st.title("Análises da DFC")
    st.caption("Análises diárias, semanais, mensais e anuais nos formatos da planilha.")
    year = selected_year()
    transactions = period_transactions(year)
    expenses = _expense_rows(transactions)
    monthly = db.get_monthly_summary(year).sort_values("month")
    annual_revenue = float(monthly["revenue"].sum())
    annual_expenses = float(monthly["expenses"].sum())
    annual_balance = annual_revenue - annual_expenses

    warning_reconciliation(year, transactions)
    daily_tab, comparison_tab, variation_tab, annual_tab, percentage_tab = st.tabs([
        "Diária e semanal", "Comparadores de despesas", "Variação das despesas",
        "Totais anuais", "Despesas / faturamento",
    ])

    with daily_tab:
        month_label = st.selectbox(
            "Mês para análise diária e semanal", MONTHS,
            index=pd.Timestamp.today().month - 1, key="analysis_daily_month",
        )
        month = MONTHS.index(month_label) + 1
        month_data = transactions[transactions["date"].dt.month == month] if not transactions.empty else transactions
        day_count = monthrange(year, month)[1]
        day_numbers = list(range(1, day_count + 1))
        day_labels = [f"{day:02d}/{month_label}" for day in day_numbers]

        def daily_values(kind: str) -> list[float]:
            if month_data.empty:
                return [0.0] * day_count
            rows = month_data[month_data["kind"] == kind]
            if rows.empty:
                return [0.0] * day_count
            totals = rows.groupby(rows["date"].dt.day)["amount"].sum()
            return [float(totals.get(day, 0.0)) for day in day_numbers]

        revenue_daily = daily_values("Receita")
        expense_daily = daily_values("Despesa")
        _show_chart(
            grouped_bar(day_labels, [revenue_daily], "Receita diária", ["Receita"], ["#2c8b4b"]),
            "Colunas diárias de receita no mês selecionado",
            "analysis_daily_revenue",
        )
        _show_chart(
            grouped_bar(day_labels, [expense_daily], "Saída diária", ["Despesas"], ["#c62b21"]),
            "Colunas diárias de despesas no mês selecionado",
            "analysis_daily_expenses",
        )

        st.subheader("Receitas e saídas por semana")
        st.caption("Semana 1: dias 1–7; semana 2: 8–14; semana 3: 15–21; semana 4: 22 até o fim do mês.")
        week_index = pd.Series(
            [min((day - 1) // 7 + 1, 4) for day in day_numbers],
            index=day_numbers,
        )
        weekly_revenue = [sum(revenue_daily[day - 1] for day in day_numbers if week_index[day] == week)
                          for week in range(1, 5)]
        weekly_expenses = [sum(expense_daily[day - 1] for day in day_numbers if week_index[day] == week)
                           for week in range(1, 5)]
        week_labels = ["Semana 1", "Semana 2", "Semana 3", "Semana 4"]
        left, right = st.columns(2)
        with left:
            _show_chart(
                grouped_bar(week_labels, [weekly_revenue], "Receita semanal", ["Receita"], ["#2c8b4b"]),
                "Colunas de receita por faixa semanal",
                "analysis_weekly_revenue",
            )
        with right:
            _show_chart(
                grouped_bar(week_labels, [weekly_expenses], "Saída semanal", ["Despesas"], ["#c62b21"]),
                "Colunas de despesas por faixa semanal",
                "analysis_weekly_expenses",
            )

    with comparison_tab:
        st.caption("Cada gráfico compara as categorias mês a mês. Use o filtro ao lado para isolar uma categoria.")
        _comparison_chart(
            expenses, "Variável", VARIABLE_ORDER,
            "Comparador de despesas variáveis", "variable_expense_comparison",
        )
        _comparison_chart(
            expenses, "Fixa", FIXED_ORDER,
            "Comparador de despesas fixas", "fixed_expense_comparison",
        )

    with variation_tab:
        st.caption("A variação compara cada mês com o mês anterior: (valor do mês ÷ valor do mês anterior) − 1. Se o mês anterior não tiver despesa, o resultado fica indisponível.")
        left, right = st.columns(2)
        with left:
            st.subheader("Despesas variáveis")
            _variation_chart(expenses, "Variável", VARIABLE_ORDER, "variable_expense_variation")
        with right:
            st.subheader("Despesas fixas")
            _variation_chart(expenses, "Fixa", FIXED_ORDER, "fixed_expense_variation")

    with annual_tab:
        cards = st.columns(3)
        cards[0].metric("Faturamento anual", brl(annual_revenue))
        cards[1].metric("Despesas anuais", brl(annual_expenses))
        cards[2].metric("Saldo final", brl(annual_balance))

        left, right = st.columns([1.4, 1])
        months = [MONTHS[int(m) - 1] for m in monthly["month"]]
        with left:
            _show_chart(
                grouped_bar(
                    months,
                    [monthly["revenue"].astype(float).tolist(), monthly["expenses"].astype(float).tolist()],
                    "Total de receita e saídas", ["Faturamento", "Despesas"],
                    ["#23864b", "#c72525"], currency=True,
                ),
                "Colunas mensais de faturamento e despesas do ano",
                "annual_revenue_expenses",
            )
        with right:
            category_totals = expenses.groupby("category_key")["amount"].sum().sort_values(ascending=False) if not expenses.empty else pd.Series(dtype=float)
            _show_chart(
                pie_chart(category_totals.index.tolist(), category_totals.values.tolist(), "Total de despesas"),
                "Gráfico de pizza da composição anual das despesas",
                "annual_expense_pie",
            )

        st.subheader("Tabela geral de despesas / porcentagem")
        categories = list(dict.fromkeys(VARIABLE_ORDER + FIXED_ORDER))
        if not expenses.empty:
            extras = sorted(set(expenses["category_key"].unique()) - set(categories))
            categories.extend(extras)
            category_amounts = expenses.groupby("category_key")["amount"].sum().to_dict()
        else:
            category_amounts = {}
        expense_detail_total = float(expenses["amount"].sum()) if not expenses.empty else 0.0
        fixed_total = float(expenses.loc[expenses["expense_type"].str.casefold() == "fixa", "amount"].sum()) if not expenses.empty else 0.0
        variable_total = float(expenses.loc[expenses["expense_type"].str.casefold() == "variável", "amount"].sum()) if not expenses.empty else 0.0
        annual_rows = [
            {"Descrição": category.title(), "Valor": float(category_amounts.get(category, 0.0)),
             "% do faturamento": _percent(float(category_amounts.get(category, 0.0)), annual_revenue),
             "% das despesas": _percent(float(category_amounts.get(category, 0.0)), annual_expenses)}
            for category in categories
        ]
        annual_rows.extend([
            {"Descrição": "Despesas variáveis", "Valor": variable_total,
             "% do faturamento": _percent(variable_total, annual_revenue),
             "% das despesas": _percent(variable_total, annual_expenses)},
            {"Descrição": "Despesas fixas", "Valor": fixed_total,
             "% do faturamento": _percent(fixed_total, annual_revenue),
             "% das despesas": _percent(fixed_total, annual_expenses)},
            {"Descrição": "Faturamento", "Valor": annual_revenue,
             "% do faturamento": _percent(annual_revenue, annual_revenue),
             "% das despesas": "—"},
            {"Descrição": "Despesas", "Valor": annual_expenses,
             "% do faturamento": _percent(annual_expenses, annual_revenue),
             "% das despesas": _percent(annual_expenses, annual_expenses)},
        ])
        annual_table = pd.DataFrame(annual_rows)
        st.dataframe(annual_table, hide_index=True, use_container_width=True, column_config={
            "Valor": st.column_config.NumberColumn(format="R$ %.2f"),
        })
        export_csv(annual_table, "Exportar tabela anual CSV", f"despesas_anuais_{year}.csv")

    with percentage_tab:
        st.caption("Cada percentual é a despesa da categoria dividida pelo faturamento do respectivo mês. Quando não há faturamento, o percentual aparece como —.")
        categories = list(dict.fromkeys(VARIABLE_ORDER + FIXED_ORDER))
        if not expenses.empty:
            categories.extend(sorted(set(expenses["category_key"].unique()) - set(categories)))
        revenue_by_month = monthly.set_index("month")["revenue"].to_dict()
        for start in range(0, 12, 3):
            cols = st.columns(3)
            for offset, col in enumerate(cols):
                month = start + offset + 1
                with col:
                    st.markdown(f"**{MONTHS[month - 1]}**")
                    table = _monthly_expense_table(
                        month, float(revenue_by_month.get(month, 0.0)), expenses, categories
                    )
                    st.dataframe(table, hide_index=True, use_container_width=True, column_config={
                        "Valor": st.column_config.NumberColumn(format="R$ %.2f"),
                    })


render()
