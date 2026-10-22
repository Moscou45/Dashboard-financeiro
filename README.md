# Painel financeiro Taqi Motos

Aplicativo em português inspirado na referência visual enviada. Inclui páginas de visão financeira, produtos, cadastro e importação de planilhas. A edição local usa SQLite; a configuração de produção usa PostgreSQL e login Google com lista autorizada de e-mails.

## Iniciar no Windows

1. Instale o Python 3.12.
2. Abra um terminal nesta pasta.
3. Execute `python -m venv .venv` e depois `.venv\Scripts\activate`.
4. Execute `pip install -r requirements.txt`.
5. Execute `streamlit run streamlit_app.py`.

Por padrão, o app usa SQLite local em `data/dashboard.db`. Para produção, configure uma URL PostgreSQL e OIDC no arquivo `.streamlit/secrets.toml` ou no painel de secrets do host. O modelo está em `.streamlit/secrets.toml.example`; nunca publique secrets nem envie o arquivo `.streamlit/secrets.toml` ao Git.

## Preparação de hospedagem

O destino definido é Streamlit Community Cloud com Supabase PostgreSQL. O Community Cloud publica apps a partir de um repositório GitHub e recebe secrets nas configurações do app. A conexão PostgreSQL do Supabase deve usar SSL; prefira o pooler indicado no painel Supabase quando o host exigir IPv4.

1. Crie um projeto PostgreSQL no Supabase e copie a URL de conexão indicada em **Connect**. Use `sslmode=require`.
2. Crie credenciais OIDC no Google Cloud para o domínio final do app; copie `client_id`, `client_secret` e cadastre a URL de callback terminada em `/oauth2callback`.
3. Use o repositório GitHub do app. Um repositório privado é preferível; o repositório indicado para este projeto é público, então o código não inclui histórico financeiro, bancos locais, lista de e-mails nem `.streamlit/secrets.toml`.
4. Publique no Streamlit Community Cloud e preencha os secrets usando o modelo. Como o repositório indicado é público, marque o app como privado nas configurações de compartilhamento antes de conectá-lo ao banco. Preencha `[authorization]` com os dois e-mails informados pelo proprietário.
5. Depois de guardar a URL PostgreSQL em `.streamlit/secrets.toml` local, rode `python seed_database.py` uma vez para carregar o histórico inicial do JSON local. A aplicação em produção não semeia nem altera dados automaticamente ao iniciar.

Não envie senhas, tokens, `client_secret` ou URL de conexão com senha no chat. Insira esses valores diretamente nos secrets do provedor. O acesso do proprietário é de edição; o e-mail autorizado como visualizador não recebe as páginas de cadastro/importação e também é bloqueado se tentar acessá-las diretamente.

## Origem dos dados iniciais

O arquivo `initial_data.json` contém registros financeiros normalizados sem descrições ou nomes de clientes. Os totais mensais vêm da aba `MES`; os detalhes de categorias e pagamentos vêm da `DFC`; os produtos vêm da tabela `Cadastro!AE383:AK3206`. Os meses sem registros permanecem sem movimento. O app sinaliza quando os detalhes de despesas não conciliam com o total consolidado mensal.

Sem secrets OIDC, a execução local mantém um seletor de perfil apenas para demonstração. Quando `APP_ENV="production"` ou um banco remoto é configurado sem OIDC válido, o app bloqueia o acesso em vez de abrir o painel sem autenticação.
