# TYVON

TYVON é um aplicativo de treino com experiência única, frontend React/Vite e backend Flask/PostgreSQL.

## Arquitetura

- Frontend: React 19 + Vite + Motion.
- Backend: Flask 3 + Gunicorn.
- Banco: PostgreSQL com dados normalizados.
- IA: gateway server-side para NVIDIA Cloud com protocolo SSE próprio do TYVON.
- Autenticação: senha Argon2id, Google OAuth/PKCE, sessão HttpOnly, CSRF e recuperação/verificação de e-mail.
- Produção: Render Web Service + Render PostgreSQL.
- Android: WebView endurecida apontando para a aplicação web publicada.

A aplicação usa uma única experiência TYVON, com identidade preto/grafite/branco e regras de treino centralizadas no motor do produto.

## Treinos

O motor TYVON é a única fonte de plano ativa.

Adultos recebem fichas completas conforme a frequência:

- 2 dias: dois treinos de corpo inteiro.
- 3 dias: três treinos de corpo inteiro.
- 4 dias: superiores/inferiores A/B.
- 5 dias: Push/Pull/Pernas/Superiores/Inferiores.

As sessões adultas usam aproximadamente seis exercícios por dia, respeitando os equipamentos disponíveis. Usuários de 14 a 17 anos usam uma programação mais conservadora, limitada a até três sessões de corpo inteiro, foco técnico e maior margem de repetições.

Cada série concluída pode registrar carga, repetições e RIR.

## Persistência

A API continua expondo `/api/account` para manter um contrato simples com o frontend, mas o estado não é mais armazenado como um único JSONB.

Tabelas principais:

- `tyvon_users`
- `tyvon_sessions`
- `tyvon_profiles`
- `tyvon_account_meta`
- `tyvon_messages`
- `tyvon_workout_logs`
- `tyvon_workout_sets`
- `tyvon_email_tokens`
- `tyvon_ai_limits`
- `tyvon_consents`
- `tyvon_privacy_requests`

O cliente usa uma revisão de estado via `If-Match` para impedir que uma aba ou dispositivo sobrescreva silenciosamente dados mais novos.

Mensagens em streaming não são gravadas token por token. O autosave ignora mensagens ainda marcadas como live e persiste apenas snapshots duráveis.

## Migrações

`backend/migrate.py` executa arquivos SQL versionados de `migrations/` antes do Gunicorn servir tráfego.

O runner usa PostgreSQL advisory lock, então múltiplos workers/processos podem iniciar sem executar DDL concorrente.

O primeiro deploy com a nova arquitetura migra o estado legado de `tyvon_accounts` para as tabelas normalizadas e mantém o registro antigo apenas como fallback histórico durante a transição.

## Segurança

- Argon2id para novas senhas.
- Hashes PBKDF2 antigos são aceitos no primeiro login válido e convertidos automaticamente para Argon2id.
- Google e senha com o mesmo e-mail são vinculados à mesma conta.
- Tokens de sessão aleatórios; somente o SHA-256 do token é persistido.
- Cookies HttpOnly e Secure em HTTPS.
- CSRF double-submit em operações autenticadas de escrita.
- origem canônica e `ProxyFix` configurável por `TRUST_PROXY_HOPS`.
- CSP, HSTS, X-Frame-Options, Referrer-Policy, Permissions-Policy, COOP e CORP.
- request ID e logging estruturado.
- falha de PostgreSQL retorna `DATABASE_UNAVAILABLE` em vez de parecer logout.
- rate limit de login, recuperação de senha e TYVON AI.
- validação server-side de objetivo, experiência e equipamentos.
- dados do perfil usados pela IA são carregados do banco, não confiados ao payload do navegador.

## IA

`POST /api/chat`:

1. valida sessão, CSRF e payload;
2. bloqueia padrões explícitos de prompt injection;
3. carrega o perfil confiável do banco;
4. resolve pedidos de ficha pelo motor TYVON antes de chamar o modelo;
5. aplica rate limit por usuário/IP;
6. chama o provedor server-side;
7. converte o stream do provedor para o protocolo TYVON:

```text
data: {"type":"token","text":"..."}
data: {"type":"done"}
```

O navegador não conhece mais o formato `choices[].delta.content` do provedor.

Limites padrão:

- 12 chamadas de IA por minuto.
- 150 chamadas de IA por dia.

Podem ser alterados por `AI_RATE_LIMIT_MINUTE` e `AI_RATE_LIMIT_DAY`.

## Conta e e-mail

O backend contém:

- verificação de e-mail;
- reenvio de verificação;
- solicitação de recuperação;
- redefinição por token de uso único;
- invalidação de sessões após redefinir senha.

O envio exige SMTP configurado. Sem SMTP, login e Google continuam funcionando, mas a UI informa que a entrega por e-mail está indisponível.

## LGPD

`POST /api/privacy/requests` cria um protocolo.

`GET /api/privacy/requests/me` mostra solicitações vinculadas ao usuário.

Opcionalmente, `PRIVACY_WEBHOOK_URL` recebe nova solicitação. Um sistema administrativo pode atualizar o status por `PATCH /api/privacy/requests/<protocol>` usando `PRIVACY_ADMIN_TOKEN`.

Status suportados:

- `received`
- `in_review`
- `completed`
- `rejected`

## Desenvolvimento

Requisitos:

- Python 3.13+
- Node.js 22+
- PostgreSQL

```bash
cp .env.example .env
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
npm ci
npm run build
python app.py
```

`npm run build` executa automaticamente testes frontend e backend antes de compilar.

## Testes

```bash
npm run test:frontend
python -m pytest -q
npm run build
```

O CI executa esses checks em pull requests e pushes para `main`.

## Variáveis

Obrigatórias em produção:

- `DATABASE_URL`
- `NVIDIA_API_KEY`
- `NVIDIA_MODEL`
- `PUBLIC_ORIGIN`
- `AUTH_BASE_URL`

Google opcional:

- `GOOGLE_CLIENT_ID`
- `GOOGLE_CLIENT_SECRET`

E-mail opcional:

- `SMTP_HOST`
- `SMTP_PORT`
- `SMTP_USERNAME`
- `SMTP_PASSWORD`
- `EMAIL_FROM`

Privacidade opcional:

- `PRIVACY_WEBHOOK_URL`
- `PRIVACY_ADMIN_TOKEN`

Operação:

- `TRUST_PROXY_HOPS`
- `AI_RATE_LIMIT_MINUTE`
- `AI_RATE_LIMIT_DAY`

Nunca use prefixo `VITE_` para segredos.

## Health checks

- `/api/health/live`: processo Flask está vivo.
- `/api/health/ready`: aplicação e PostgreSQL estão prontos.
- `/api/health`: alias da readiness.

## Build de produção

```bash
pip install -r requirements.txt && npm ci && npm run build
gunicorn --bind 0.0.0.0:$PORT --workers 2 --threads 4 --timeout 90 wsgi:app
```
