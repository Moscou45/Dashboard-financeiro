# Painel financeiro Taqi Motos

Aplicativo em portugu�s inspirado na refer�ncia visual enviada. Inclui p�ginas de vis�o financeira, produtos, cadastro e importa��o de planilhas. A edi��o local usa SQLite; a configura��o de produ��o usa PostgreSQL e login Google com lista autorizada de e-mails.

## Iniciar no Windows

1. Instale o Python 3.12.
2. Abra um terminal nesta pasta.
3. Execute `python -m venv .venv` e depois `.venv\Scripts\activate`.
4. Execute `pip install -r requirements.txt`.
5. Execute `streamlit run streamlit_app.py`.

Por padr�o, o app usa SQLite local em `data/dashboard.db`. Para produ��o, configure uma URL PostgreSQL e OIDC no arquivo `.streamlit/secrets.toml` ou no painel de secrets do host. O modelo est� em `.streamlit/secrets.toml.example`; nunca publique secrets nem envie o arquivo `.streamlit/secrets.toml` ao Git.

## Prepara��o de hospedagem

O destino definido � Streamlit Community Cloud com Supabase PostgreSQL. O Community Cloud publica apps a partir de um reposit�rio GitHub e recebe secrets nas configura��es do app. A conex�o PostgreSQL do Supabase deve usar SSL; prefira o pooler indicado no painel Supabase quando o host exigir IPv4.

1. Crie um projeto PostgreSQL no Supabase e copie a URL de conex�o indicada em **Connect**. Use `sslmode=require`.
2. Crie credenciais OIDC no Google Cloud para o dom�nio final do app; copie `client_id`, `client_secret` e cadastre a URL de callback terminada em `/oauth2callback`.
3. Use o reposit�rio GitHub do app. Um reposit�rio privado � prefer�vel; o reposit�rio indicado para este projeto � p�blico, ent�o o c�digo n�o inclui hist�rico financeiro, bancos locais, lista de e-mails nem `.streamlit/secrets.toml`.
4. Publique no Streamlit Community Cloud e preencha os secrets usando o modelo. Como o reposit�rio indicado � p�blico, marque o app como privado nas configura��es de compartilhamento antes de conect�-lo ao banco. Preencha `[authorization]` com os dois e-mails informados pelo propriet�rio.
5. O propriet�rio pode carregar o hist�rico pela p�gina **Importar planilha**, enviando o JSON normalizado e conferindo as quantidades antes de clicar em **Importar hist�rico para o PostgreSQL**. A carga � transacional e s� acontece se as tabelas de resumo, movimenta��es e produtos estiverem vazias. Como alternativa para opera��o local, configure a URL PostgreSQL em `.streamlit/secrets.toml` e execute `python seed_database.py`. A aplica��o n�o importa dados automaticamente ao iniciar.

N�o envie senhas, tokens, `client_secret` ou URL de conex�o com senha no chat. Insira esses valores diretamente nos secrets do provedor. O acesso do propriet�rio � de edi��o; o e-mail autorizado como visualizador n�o recebe as p�ginas de cadastro/importa��o e tamb�m � bloqueado se tentar acess�-las diretamente.

## Origem dos dados iniciais

O arquivo `initial_data.json` cont�m registros financeiros normalizados sem descri��es ou nomes de clientes. Os totais mensais v�m da aba `MES`; os detalhes de categorias e pagamentos v�m da `DFC`; os produtos v�m da tabela `Cadastro!AE383:AK3206`. Os meses sem registros permanecem sem movimento. O app sinaliza quando os detalhes de despesas n�o conciliam com o total consolidado mensal.

Sem secrets OIDC, a execu��o local mant�m um seletor de perfil apenas para demonstra��o. Quando `APP_ENV="production"` ou um banco remoto � configurado sem OIDC v�lido, o app bloqueia o acesso em vez de abrir o painel sem autentica��o.
