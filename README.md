# Gerenciador de Tarefas Colaborativo (Flask)

Aplicação web segura construída com Flask, seguindo o padrão MVC, com autenticação por sessão (Flask-Login), APIs protegidas por JWT, opção de OAuth (placeholders), proteção contra XSS/CSRF/SQL Injection, drag-and-drop de tarefas, histórico de alterações, @menções com notificação por e-mail, e exportação CSV/PDF.

## Funcionalidades
- Autenticação segura: registro, login/logout, alteração de senha (hash com Werkzeug)
- Sessões com Flask-Login e endpoints REST com JWT (emissão de token pós-login)
- OAuth Google/GitHub (placeholders; configure via variáveis de ambiente)
- Proteções de segurança: SQLAlchemy (parametrizado), CSRF (Flask-WTF), XSS (Jinja + `bleach`)
- MVC: `app/models.py`, `app/controllers/*`, `app/templates/*`
- UI com Bootstrap responsiva + mensagens flash
- Kanban com drag-and-drop (JS + API Flask)
- Histórico de alterações (mover/criar/menções)
- @Menções em descrições com envio de e-mail para usuários mencionados
- Exportação de tarefas para CSV e PDF (sem SSRF)

## Requisitos
- Python 3.10+

## Como executar
1. Clone e entre no diretório do projeto.
2. Crie um ambiente virtual e instale as dependências:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
3. Configure variáveis de ambiente (copie `.env.example` para `.env` e ajuste):
   ```bash
   cp .env.example .env
   ```
   - Para desenvolvimento, por padrão usa SQLite no diretório `instance/`.
   - Para PostgreSQL: defina `DATABASE_URL=postgresql+psycopg2://user:pass@host:5432/dbname`.
   - Para MySQL: `DATABASE_URL=mysql+pymysql://user:pass@host:3306/dbname`.
4. Inicialize o banco:
   ```bash
   flask --app run.py db init
   flask --app run.py db migrate -m "init"
   flask --app run.py db upgrade
   ```
5. Inicie um servidor SMTP de desenvolvimento (opcional) para ver e-mails no console:
   ```bash
   python -m smtpd -c DebuggingServer -n localhost:1025
   ```
6. Rode a aplicação:
   ```bash
   python run.py
   ```
7. Acesse `http://localhost:5000`. Registre-se, faça login e use o quadro kanban.

## Fluxos para apresentação
- Registro e login: páginas `/register` e `/login`
- Áreas protegidas: quadro em `/` exige autenticação
- Alteração de senha: `/change-password`
- Logout: `/logout`
- Mensagens de erro e sucesso: via flash

## Segurança
- CSRF: formulários usam `{{ form.hidden_tag() }}` e proteção global via `CSRFProtect`
- XSS: Jinja2 autoescape e sanitização com `bleach` de entradas ricas
- SQL Injection: SQLAlchemy com consultas parametrizadas
- Senhas com hash forte: `werkzeug.security`
- JWT para APIs: `flask-jwt-extended` com expiração curta e header Authorization
- SSRF: exportação gera CSV/PDF localmente, sem buscar URLs externas

## OAuth (opcional)
- Configure `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GITHUB_CLIENT_ID`, `GITHUB_CLIENT_SECRET` e `OAUTH_REDIRECT_URI`
- Endpoints de login estão prontos, mas retornam aviso até que credenciais sejam fornecidas

## Estrutura
- `app/__init__.py`: app factory e registro de blueprints
- `app/extensions.py`: instâncias de extensões
- `app/models.py`: modelos `User`, `Task`, `TaskHistory`
- `app/controllers/`: rotas de autenticação, páginas e APIs
- `app/templates/`: templates Jinja2 (Bootstrap)
- `app/static/js/board.js`: drag-and-drop
- `app/static/css/styles.css`: estilos do kanban

## Notas
- Para produção, defina `SECRET_KEY` e `JWT_SECRET_KEY` fortes e configure banco externo.
- Ative HTTPS em produção para proteger cookies/headers.