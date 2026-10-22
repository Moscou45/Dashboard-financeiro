"""Importa a fotografia inicial da planilha para o PostgreSQL configurado.

Execute localmente depois de preencher as credenciais em .streamlit/secrets.toml.
O processo é idempotente e não modifica o arquivo Excel original.
"""

import db


if __name__ == "__main__":
    if db.engine.dialect.name == "sqlite":
        raise SystemExit("Configure a URL do PostgreSQL no ambiente ou em .streamlit/secrets.toml antes de importar.")
    db.initialize()
    if db.seed_remote_data():
        print("Histórico inicial importado para o PostgreSQL.")
    else:
        print("Banco já inicializado ou arquivo initial_data.json indisponível; nenhuma linha foi alterada.")
