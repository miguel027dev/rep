# REP — backup Flask/PostgreSQL

Este backup contém o frontend React/Vite original e a camada de backend migrada para Flask + PostgreSQL.

Para restaurar: configure `DATABASE_URL`, instale `requirements.txt` e dependências npm, rode `npm run build` e inicie `gunicorn ... wsgi:app` (ou `python app.py` localmente).

As credenciais reais de NVIDIA/Google não fazem parte do repositório. Configure-as como variáveis de ambiente no servidor.

Consulte `README.md` para arquitetura, segurança, testes, banco e deploy no Render.
