import streamlit as st

import db
from auth import require_editor


def render():
    require_editor()
    st.title("Reiniciar dados")
    st.caption("Limpe o histórico para começar a cadastrar os dados atuais da empresa.")
    if db.engine.dialect.name != "postgresql":
        st.info("Esta limpeza fica disponível somente no banco de dados online.")
        return

    st.warning("Esta ação apagará permanentemente todas as movimentações financeiras, os resumos mensais e as vendas de produtos do app.")
    st.write("As planilhas originais não serão alteradas. Depois da limpeza, os gráficos serão preenchidos com os novos cadastros.")
    confirmed = st.checkbox("Entendo que a limpeza não pode ser desfeita.", key="confirm_reset_all_data")
    if st.button("Apagar todos os dados", type="primary", disabled=not confirmed):
        try:
            deleted = db.clear_all_data()
        except Exception:
            st.error("A limpeza falhou. Nenhum dado foi confirmado como removido. Confira os logs do app.")
        else:
            st.success(
                "Dados removidos: "
                + str(deleted["transactions"]) + " movimentações, "
                + str(deleted["monthly_summary"]) + " resumos mensais e "
                + str(deleted["product_sales"]) + " vendas de produtos."
            )


render()
