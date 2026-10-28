from __future__ import annotations

from collections.abc import Sequence

import numpy as np
import plotly.graph_objects as go

BLUE = "#4f63f5"
TEAL = "#20b486"
RED = "#e36578"
GOLD = "#f1a33c"
PURPLE = "#8b6fe8"
SKY = "#49a4c8"
PALETTE = [BLUE, TEAL, GOLD, RED, PURPLE, SKY, "#8b9bb4", "#d26ca5"]
CHART_CONFIG = {"displayModeBar": "hover", "displaylogo": False, "responsive": True}


def _layout(fig: go.Figure, title: str, height: int = 380) -> go.Figure:
    fig.update_layout(
        title={"text": title, "x": 0.015, "xanchor": "left", "font": {"size": 16, "color": "#172033"}},
        template="plotly_white",
        height=height,
        margin={"l": 18, "r": 18, "t": 62, "b": 28},
        font={"family": "Inter, Arial, sans-serif", "size": 12, "color": "#526078"},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        hoverlabel={"bgcolor": "#172033", "font": {"color": "white", "size": 12}, "bordercolor": "#172033"},
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.02, "x": 0, "xanchor": "left", "title_text": ""},
        hovermode="x unified",
    )
    fig.update_xaxes(showgrid=False, zeroline=False, linecolor="#e8edf4", tickfont={"color": "#68758b"})
    fig.update_yaxes(showgrid=True, gridcolor="#edf1f6", zeroline=False, linecolor="rgba(0,0,0,0)", tickfont={"color": "#68758b"})
    return fig


def _money_hover(series: str) -> str:
    return f"<b>{series}</b><br>%{{x}}<br>R$ %{{y:,.2f}}<extra></extra>"


def financial_overview(labels: Sequence[str], revenue: Sequence[float], expenses: Sequence[float], balance: Sequence[float]) -> go.Figure:
    fig = go.Figure()
    fig.add_bar(x=list(labels), y=list(revenue), name="Receitas", marker_color=BLUE, marker_line_width=0, hovertemplate=_money_hover("Receitas"))
    fig.add_bar(x=list(labels), y=list(expenses), name="Despesas", marker_color=RED, marker_line_width=0, hovertemplate=_money_hover("Despesas"))
    fig.add_scatter(x=list(labels), y=list(balance), name="Saldo", mode="lines+markers", line={"color": TEAL, "width": 3}, marker={"size": 7, "line": {"color": "white", "width": 1.5}}, hovertemplate=_money_hover("Saldo"))
    fig.update_layout(barmode="group", bargap=0.28, bargroupgap=0.12)
    fig.update_yaxes(tickprefix="R$ ", tickformat="~s", separatethousands=True)
    return _layout(fig, "Receitas, despesas e saldo por mês", 420)


def donut_chart(labels: Sequence[str], values: Sequence[float], title: str) -> go.Figure:
    clean = [(str(label), float(value)) for label, value in zip(labels, values) if np.isfinite(value) and float(value) > 0]
    fig = go.Figure()
    if clean:
        names, amounts = zip(*clean)
        total = sum(amounts)
        fig.add_trace(go.Pie(
            labels=list(names), values=list(amounts), hole=0.66, sort=False,
            marker={"colors": PALETTE, "line": {"color": "white", "width": 3}},
            textinfo="percent", textposition="inside", insidetextfont={"color": "white", "size": 12},
            hovertemplate="<b>%{label}</b><br>R$ %{value:,.2f}<br>%{percent}<extra></extra>",
            showlegend=True,
        ))
        fig.add_annotation(x=0.5, y=0.5, text=f"<b>R$ {total:,.0f}</b><br><span style='font-size:11px;color:#8792a5'>total</span>", showarrow=False, font={"size": 16, "color": "#172033"})
    else:
        fig.add_annotation(x=0.5, y=0.52, text="Sem dados no período", showarrow=False, font={"size": 13, "color": "#8792a5"})
    fig.update_layout(
        title={"text": title, "x": 0.015, "xanchor": "left", "font": {"size": 16, "color": "#172033"}},
        height=360, margin={"l": 12, "r": 12, "t": 56, "b": 54},
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font={"family": "Inter, Arial, sans-serif", "size": 11, "color": "#526078"},
        legend={"orientation": "h", "yanchor": "top", "y": -0.12, "xanchor": "left", "x": 0, "font": {"size": 10}},
        hoverlabel={"bgcolor": "#172033", "font": {"color": "white"}},
    )
    return fig


def grouped_bar(labels: Sequence[str], series: Sequence[Sequence[float]], title: str, series_names: Sequence[str], colors: Sequence[str] | None = None, currency: bool = True, horizontal: bool = False) -> go.Figure:
    colors = list(colors or PALETTE)
    fig = go.Figure()
    for index, values in enumerate(series):
        name = series_names[index] if index < len(series_names) else f"Série {index + 1}"
        color = colors[index % len(colors)]
        if horizontal:
            fig.add_bar(y=list(labels), x=list(values), name=name, orientation="h", marker_color=color, marker_line_width=0, hovertemplate=f"<b>{name}</b><br>%{{y}}<br>" + ("R$ " if currency else "") + "%{x:,.2f}<extra></extra>")
        else:
            fig.add_bar(x=list(labels), y=list(values), name=name, marker_color=color, marker_line_width=0, hovertemplate=f"<b>{name}</b><br>%{{x}}<br>" + ("R$ " if currency else "") + "%{y:,.2f}<extra></extra>")
    fig.update_layout(barmode="group", bargap=0.3, bargroupgap=0.1)
    if horizontal:
        fig.update_yaxes(autorange="reversed")
        fig.update_xaxes(tickprefix="R$ " if currency else "", tickformat="~s" if currency else ",.0f", separatethousands=True)
        return _layout(fig, title, max(340, 28 * len(labels) + 110))
    fig.update_yaxes(tickprefix="R$ " if currency else "", tickformat="~s" if currency else ",.0f", separatethousands=True)
    return _layout(fig, title, 380)


def variation_chart(labels: Sequence[str], revenue_change: Sequence[float], expense_change: Sequence[float]) -> go.Figure:
    fig = go.Figure()
    fig.add_scatter(x=list(labels), y=list(revenue_change), name="Receitas", mode="lines+markers", connectgaps=False, line={"color": BLUE, "width": 3}, marker={"size": 7}, hovertemplate="<b>Receitas</b><br>%{x}<br>%{y:.1f}%<extra></extra>")
    fig.add_scatter(x=list(labels), y=list(expense_change), name="Despesas", mode="lines+markers", connectgaps=False, line={"color": RED, "width": 3}, marker={"size": 7}, hovertemplate="<b>Despesas</b><br>%{x}<br>%{y:.1f}%<extra></extra>")
    fig.add_hline(y=0, line_color="#aeb8c7", line_width=1)
    fig.update_yaxes(ticksuffix="%", zeroline=False)
    return _layout(fig, "Variação mensal em relação ao mês anterior", 360)


def payment_chart(labels: Sequence[str], series: Sequence[Sequence[float]], names: Sequence[str]) -> go.Figure:
    fig = go.Figure()
    for index, (name, values) in enumerate(zip(names, series)):
        fig.add_bar(x=list(labels), y=list(values), name=str(name), marker_color=PALETTE[index % len(PALETTE)], marker_line_width=0, hovertemplate=f"<b>{name}</b><br>%{{x}}<br>R$ %{{y:,.2f}}<extra></extra>")
    fig.update_layout(barmode="stack", bargap=0.32)
    fig.update_yaxes(tickprefix="R$ ", tickformat="~s", separatethousands=True)
    return _layout(fig, "Valores por forma de pagamento", 380)

