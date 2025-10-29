# Backend - Restaurant Analytics API

FastAPI backend para a plataforma de analytics.

## Setup Local

```bash
# Instalar dependências
pip install -r requirements.txt

# Rodar servidor (com hot reload)
uvicorn app.main:app --reload --port 8000
```

## Estrutura

```
app/
├── api/          # API routes e endpoints
├── core/         # Configuração, DB, Cache
├── models/       # Schemas Pydantic
└── services/     # Lógica de negócio
```

## Testes

```bash
pytest
pytest --cov=app --cov-report=html
```

## API Docs

http://localhost:8000/docs

