# SISAV 2

Sistema de Serviços Acadêmicos da UEM — reestruturação do SISAV.
Construção de Software 2026.

## Stack

| Camada | Tecnologia |
|---|---|
| Backend | Python 3.12 · FastAPI · SQLAlchemy 2.0 (async) · Alembic |
| Frontend | Vite · React 19 · TypeScript · Tailwind v4 · shadcn/ui |
| Persistência/Dados | PostgreSQL 16 · FileStore |
| Infra | Docker Compose · GitHub Actions |

## Como rodar

```bash
cp .env.example .env   # opcional — já existem defaults seguros para dev
make up                # sobe banco + backend + frontend
```

| Onde | URL |
|---|---|
| Aplicação | http://localhost:5173 |
| API docs (Swagger) | http://localhost:8000/docs |
| Health | http://localhost:8000/health |

## Comandos úteis

| Comando | O que faz |
|---|---|
| `make up` / `make down` | sobe / derruba os serviços |
| `make logs` | logs do backend |
| `make migrate` | aplica migrations (`alembic upgrade head`) |
| `make test` | testes do backend + typecheck do frontend |
| `make backend-test` / `make frontend-lint` | por lado |

## Estrutura

```
sisav2/
├─ backend/          # API — pacote src/sisav
│   └─ src/sisav/
│       ├─ main.py   # FastAPI + /health
│       ├─ core/     # config (settings) e db (engine/sessão async, Base)
│       └─ modules/  # (a criar) domínios do monólito modular
|   └─ uploads/     # FileStore (Armazenamento local de PDFs e comprovantes)
├─ frontend/         # SPA Vite + React
├─ .github/          # CI (ruff + pytest + typecheck/build)
├─ docker-compose.yml · Makefile · .env.example
└─ docs/diagramas/   # fontes Mermaid dos diagramas arquiteturais
```

## Documentação do trabalho

A documentação (requisitos, decisões, atas) fica no **Notion**; o tracking
Scrum (backlog e sprint) fica no **Linear**. O repositório mantém apenas
código, o README e os diagramas PlantUML em `docs/diagramas/`.

## Equipe

Daniella Midori Hamada Yamasaki · Gabriel Rodrigues Gomes ·
Gabrielly Bianka Ferreira da Mata · João Vitor Bidoia Angelo

## Links

- Notion: a preencher
- Linear: a preencher
