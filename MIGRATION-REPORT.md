# REP — relatório de migração

## Objetivo

Migrar o backend do REP de Cloudflare Worker + D1 para Flask + PostgreSQL sem alterar o design/frontend.

## Resultado

- Backend principal: Flask.
- Banco: PostgreSQL (`JSONB` para o estado da conta).
- Produção: Gunicorn.
- Streaming do chat NVIDIA: mantido via SSE no mesmo endpoint `/api/chat`.
- Autenticação por e-mail/senha e Google OAuth: contratos HTTP preservados.
- Frontend: `src/` e `public/` não foram editados.

## Verificação de integridade do frontend

Foi calculado SHA-256 de todos os arquivos em `src/` e `public/` antes da migração e novamente depois. O `diff` dos dois manifestos ficou vazio: **100% dos arquivos são byte a byte idênticos**.

## Testes executados localmente

- 7/7 testes Node puros de onboarding, tema e regras de treino: aprovados.
- `python -m py_compile` em todo o backend Flask: aprovado.
- Comparação automática da geração/seleção de treinos Python vs JavaScript em múltiplos perfis: **equivalência 1:1 aprovada**.

O ambiente de execução usado para a migração não consegue resolver `registry.npmjs.org`, então o build Vite completo não pôde baixar dependências localmente. O `render.yaml` executa `npm ci`, testes frontend, `pytest` e `npm run build` durante o build no Render; qualquer falha impede a publicação.

## Render

Em 1 de outubro de 2026 foi criado no workspace `miguelpinxs@gmail.com` o PostgreSQL `rep-db`, plano free, região Oregon, PostgreSQL 18. O banco ficou com status `available`.

A conexão externa do banco permanece bloqueada (allowlist vazia), que é a configuração mais segura. O Web Service deve usar a URL interna do banco via `DATABASE_URL`.

## Segredos

O backup original não continha valores reais para `NVIDIA_API_KEY`, `GOOGLE_CLIENT_ID` ou `GOOGLE_CLIENT_SECRET`. Nenhum segredo foi inserido no repositório. Esses valores devem existir apenas nas variáveis de ambiente do Render.
