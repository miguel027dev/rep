# REP — Flask + PostgreSQL

Aplicativo REP com o frontend React/Vite original preservado e backend migrado para **Flask** com **PostgreSQL**.

## Arquitetura

- Frontend: React 19 + Vite + Motion + Three.js.
- Backend: Flask 3, servido por Gunicorn em produção.
- Banco: PostgreSQL com `psycopg` e estado de conta armazenado em `JSONB`.
- IA: NVIDIA Cloud API via `/v1/chat/completions`, com streaming SSE até o frontend.
- Autenticação: e-mail/senha com PBKDF2-SHA256, cookies HttpOnly e suporte opcional a Google OAuth/PKCE.
- Deploy: Render Web Service + Render PostgreSQL.

O frontend continua chamando os mesmos contratos HTTP (`/api/auth/*`, `/api/account`, `/api/chat`), portanto a migração não exige mudança de layout, CSS ou componentes visuais.

## Estrutura principal

- `src/` e `public/`: frontend original.
- `backend/auth.py`: autenticação, sessões e Google OAuth.
- `backend/account.py`: persistência e validação do perfil/histórico.
- `backend/chat.py`: proxy seguro para a NVIDIA e streaming SSE.
- `backend/workouts.py`: regras de treinos/cards usadas pelo backend Flask.
- `backend/db.py`: conexão e inicialização do PostgreSQL.
- `migrations/001_init.sql`: esquema SQL documentado.
- `app.py`: aplicação Flask e entrega do build Vite.
- `render.yaml`: referência de infraestrutura para Render.

## Rodar localmente

Requisitos: Python 3.13+, Node.js 22+ e PostgreSQL.

```bash
cp .env.example .env
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
npm ci
npm run build
python app.py
```

Para desenvolver o frontend com hot reload, rode o Flask em `:5000` e, em outro terminal, `npm run dev`. O Vite faz proxy de `/api` para o Flask sem alterar o frontend.

## Variáveis de ambiente

Nunca use prefixo `VITE_` para segredos.

- `DATABASE_URL`: URL PostgreSQL.
- `NVIDIA_API_KEY`: chave server-side da NVIDIA Cloud.
- `NVIDIA_MODEL`: identificador do modelo configurado no provedor de IA.
- `GOOGLE_CLIENT_ID`: opcional.
- `GOOGLE_CLIENT_SECRET`: opcional.
- `AUTH_BASE_URL`: URL pública do serviço, usada no callback OAuth.
- `PORT`: porta local; no Render é fornecida pela plataforma.

O ZIP de origem não continha credenciais reais da NVIDIA nem do Google; somente nomes de variáveis. Elas devem ser configuradas diretamente no Render e nunca commitadas.

## Banco PostgreSQL

O backend inicializa as tabelas idempotentemente no primeiro request com `DATABASE_URL` disponível. O mesmo esquema está em `migrations/001_init.sql` para auditoria e operação manual.

Tabelas:

- `rep_users`
- `rep_sessions`
- `rep_oauth`
- `rep_auth_limits`
- `rep_accounts`

`rep_accounts.state` usa `JSONB` para manter compatibilidade com o formato de estado já esperado pelo frontend.

## Privacidade e LGPD

- `/privacidade`: Política de Privacidade pública, com categorias de dados, finalidades, bases legais, direitos do titular, fornecedores, retenção, segurança e transferências internacionais.
- `/termos`: Termos de Uso públicos.
- `POST /api/privacy/requests`: canal para solicitações de titulares com protocolo e persistência em PostgreSQL.
- `rep_privacy_requests`: tabela de acompanhamento das solicitações LGPD.
- O cadastro vincula a aceitação aos Termos e à Política de Privacidade.
- Informações de lesão, dor ou limitação são opcionais e recebem aviso específico de tratamento por poderem envolver dados sensíveis.

## Segurança

- Sessões usam tokens aleatórios; somente SHA-256 do token é salvo no banco.
- Senhas usam PBKDF2-SHA256 com 100.000 iterações e salt por usuário.
- Cookies de sessão são `HttpOnly`, `SameSite=Lax` e `Secure` em HTTPS.
- Limite de tentativas de login é persistido no PostgreSQL.
- A chave NVIDIA nunca é enviada ao browser.
- O backend limita tamanho e formato das mensagens antes de chamar o provedor.
- Erros do provedor não expõem conteúdo privado nem credenciais.

## Build e testes

```bash
npm ci
npm run build
npm run test:frontend
pytest -q
```

`npm run test:frontend` valida a lógica que continua no lado do frontend/shared. Os testes Python validam a implementação migrada do backend. A verificação de preservação visual é feita comparando SHA-256 de todos os arquivos em `src/` e `public/` antes e depois da migração.

## Deploy no Render

Build command:

```bash
pip install -r requirements.txt && npm ci && npm run build
```

Start command:

```bash
gunicorn --bind 0.0.0.0:$PORT --workers 2 --threads 4 --timeout 90 wsgi:app
```

Health check: `/api/health`.

O serviço web deve receber `DATABASE_URL` do PostgreSQL do Render e `AUTH_BASE_URL` apontando para a URL pública final.

## Migração realizada

A implementação anterior baseada em Cloudflare Worker/D1 foi substituída na camada de backend. Arquivos ativos de Worker, Drizzle e D1 foram removidos do runtime. O frontend original foi mantido sem alterações em `src/` e `public/`.
