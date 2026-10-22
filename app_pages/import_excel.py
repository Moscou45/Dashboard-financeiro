from __future__ import annotations

import hashlib
from datetime import date, datetime
from io import BytesIO

import pandas as pd
import streamlit as st

import db
from auth import require_editor


def _number(value):
    if pd.isna(value) or value == "":
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    value = str(value).strip().replace("R$", "").replace(" ", "")
    if "," in value:
        value = value.replace(".", "").replace(",", ".")
    return float(value)


def _date(value):
    if isinstance(value, (datetime, date, pd.Timestamp)):
        return pd.Timestamp(value).date().isoformat()
    return pd.to_datetime(value, dayfirst=True, errors="raise").date().isoformat()


def _dedupe(kind: str, row: dict) -> str:
    return hashlib.sha256((kind + "|" + "|".join(str(row.get(k, "")) for k in sorted(row))).encode("utf-8")).hexdigest()


def render():
    require_editor()
    st.title("Importar planilha")
    st.caption("Importe registros financeiros ou vendas de produtos de uma planilha Excel. A importação não altera o arquivo enviado.")
    uploaded = st.file_uploader("Selecione um arquivo .xlsx ou .xlsm", type=["xlsx", "xlsm"])
    if uploaded is None:
        st.info("Escolha uma planilha para começar. Você poderá selecionar a aba, mapear as colunas e conferir uma prévia antes de importar.")
        return
    try:
        workbook = pd.ExcelFile(BytesIO(uploaded.getvalue()))
    except Exception as exc:
        st.error(f"Não consegui abrir essa planilha: {exc}")
        return
    sheet = st.selectbox("Aba da planilha", workbook.sheet_names)
    header_row = st.number_input("Linha dos nomes das colunas", min_value=1, value=1, step=1)
    try:
        df = pd.read_excel(workbook, sheet_name=sheet, header=int(header_row)-1)
    except Exception as exc:
        st.error(f"Não consegui ler essa aba: {exc}")
        return
    df = df.dropna(how="all")
    if df.empty:
        st.warning("A aba selecionada não contém linhas de dados.")
        return
    df.columns = [str(c).strip() for c in df.columns]
    mode = st.radio("Tipo de dados", ["Movimentações financeiras", "Vendas de produtos"], horizontal=True)
    st.dataframe(df.head(8), hide_index=True, use_container_width=True)
    cols = df.columns.tolist()
    if mode == "Movimentações financeiras":
        st.markdown("Mapeie as colunas obrigatórias e, se existirem, as opcionais.")
        a,b,c = st.columns(3)
        date_col = a.selectbox("Data *", cols, key="tx_date")
        amount_col = b.selectbox("Valor *", cols, key="tx_amount")
        type_col = c.selectbox("Tipo (Receita/Despesa) *", cols, key="tx_type")
        a,b,c = st.columns(3)
        category_col = a.selectbox("Categoria", ["—"]+cols, key="tx_category")
        payment_col = b.selectbox("Forma de pagamento", ["—"]+cols, key="tx_payment")
        expense_col = c.selectbox("Classificação Fixa/Variável", ["—"]+cols, key="tx_expense")
        if st.button("Validar importação", type="primary"):
            rows=[]; errors=[]
            for idx, raw in df.iterrows():
                try:
                    typ = str(raw[type_col]).strip().casefold()
                    if typ in ["receita", "entrada", "income", "r"]: kind="Receita"
                    elif typ in ["despesa", "saída", "saida", "expense", "d"]: kind="Despesa"
                    else: raise ValueError("tipo deve indicar Receita ou Despesa")
                    row={"date":_date(raw[date_col]), "kind":kind, "amount":abs(_number(raw[amount_col])),
                         "category":str(raw[category_col]).strip() if category_col!="—" and pd.notna(raw[category_col]) else kind,
                         "payment_method":str(raw[payment_col]).strip() if payment_col!="—" and pd.notna(raw[payment_col]) else None,
                         "expense_type":str(raw[expense_col]).strip().capitalize() if expense_col!="—" and pd.notna(raw[expense_col]) else None}
                    row["dedupe_key"]=_dedupe("finance", row)
                    rows.append(row)
                except Exception as exc: errors.append(f"Linha {idx+int(header_row)+1}: {exc}")
            st.session_state["pending_import"]={"kind":"finance", "rows":rows, "errors":errors}
    else:
        st.markdown("Informe nome, quantidade, custo e receita. O lucro será calculado como receita menos custo.")
        a,b,c = st.columns(3)
        product_col = a.selectbox("Produto *", cols, key="p_name")
        qty_col = b.selectbox("Quantidade *", cols, key="p_qty")
        revenue_col = c.selectbox("Receita *", cols, key="p_revenue")
        a,b,c = st.columns(3)
        cost_col = a.selectbox("Custo *", cols, key="p_cost")
        date_col = b.selectbox("Data ou mês *", cols, key="p_date")
        year_default = c.number_input("Ano (se não houver data)", min_value=2000, max_value=2100, value=2026)
        if st.button("Validar importação", type="primary"):
            rows=[]; errors=[]
            for idx, raw in df.iterrows():
                try:
                    value=raw[date_col]
                    try:
                        dt=pd.to_datetime(value, dayfirst=True, errors="raise")
                        year=int(dt.year); month=int(dt.month); label=dt.strftime("%B")
                    except Exception:
                        label=str(value).strip(); year=int(year_default)
                        names={"janeiro":1,"fevereiro":2,"março":3,"marco":3,"abril":4,"maio":5,"junho":6,"julho":7,"agosto":8,"setembro":9,"outubro":10,"novembro":11,"dezembro":12}
                        month=names.get(label.casefold())
                    row={"year":year,"month_num":month,"month_label":label,"product":str(raw[product_col]).strip(),
                         "quantity":_number(raw[qty_col]),"cost":_number(raw[cost_col]),"revenue":_number(raw[revenue_col])}
                    row["dedupe_key"]=_dedupe("product",row); rows.append(row)
                except Exception as exc: errors.append(f"Linha {idx+int(header_row)+1}: {exc}")
            st.session_state["pending_import"]={"kind":"product","rows":rows,"errors":errors}
    pending=st.session_state.get("pending_import")
    if pending:
        st.divider()
        st.subheader("Conferência antes de importar")
        st.write(f"{len(pending['rows'])} linhas válidas • {len(pending['errors'])} linhas com problemas")
        if pending["errors"]:
            with st.expander("Ver linhas com problemas"):
                st.write("\n".join(pending["errors"][:50]))
        if pending["rows"]:
            st.dataframe(pd.DataFrame(pending["rows"]).drop(columns="dedupe_key").head(10), hide_index=True, use_container_width=True)
            if st.button("Importar linhas válidas", type="primary"):
                inserted, skipped = (db.import_financial_rows(pending["rows"]) if pending["kind"]=="finance" else db.import_product_rows(pending["rows"]))
                st.session_state.pop("pending_import",None)
                st.success(f"Importação concluída: {inserted} novos registros; {skipped} duplicados ignorados.")
                st.rerun()
