# 🍔 Restaurant Analytics Platform

> Plataforma de analytics customizável para donos de restaurantes explorarem seus dados operacionais.

**Desenvolvido para:** [Nola God Level Coder Challenge](https://github.com/lucasvieira94/nola-god-level)

---

## 📋 Sobre o Projeto

Esta é uma solução completa de analytics para restaurantes, permitindo que donos como "Maria" (persona do desafio) possam:

- ✅ Visualizar métricas relevantes (faturamento, produtos mais vendidos, horários de pico)
- ✅ Criar análises personalizadas sobre múltiplos canais (presencial, iFood, Rappi, etc.)
- ✅ Comparar períodos e identificar tendências
- ✅ Extrair insights acionáveis de dados complexos

**Problema resolvido:** Donos de restaurantes têm os dados, mas não conseguem explorá-los de forma intuitiva.

---

## 🏗️ Arquitetura

```
Frontend (React + Vite)
    ↓ HTTP/REST
Backend (FastAPI + Python)
    ↓ SQL
Cache (Redis) + Database (PostgreSQL)
```

### Stack Tecnológica

| Camada | Tecnologia | Justificativa |
|--------|-----------|---------------|
| **Frontend** | React 18 + Vite + TypeScript | Performance, DX, ecosystem |
| **Data Fetching** | TanStack Query | Cache automático, performance |
| **Visualizações** | Recharts | Declarativo, performático |
| **UI** | TailwindCSS | Utility-first, produtividade |
| **Backend** | FastAPI + Python 3.11 | Async, type-safe, analytics |
| **Database** | PostgreSQL 15 | JSONB, window functions, MVs |
| **Cache** | Redis 7 | In-memory, < 1ms latency |
| **Deploy** | Railway / Render | Fácil, free tier, CI/CD |

📚 **Documentação completa:** [TECH_STACK.md](./TECH_STACK.md)

---

## 🚀 Quick Start

### Pré-requisitos

- Docker Desktop
- Node.js 18+ (para development frontend)
- Python 3.11+ (para development backend)

### 1. Clone e Setup

```bash
git clone https://github.com/genisfco/nola-analytics-god-level-challenge.git
cd nola-analytics-god-level-challenge
```

### 2. Gere os Dados (primeira vez)

```bash
# Suba apenas o PostgreSQL
docker compose up -d postgres

# Aguarde inicializar (10s)
timeout 10

# Gere ~550k vendas (10-15 min)
docker compose run --rm data-generator

# Verifique
docker compose exec postgres psql -U challenge challenge_db -c "SELECT COUNT(*) FROM sales;"
```

### 3. Suba os Serviços

```bash
# Suba tudo (PostgreSQL, Redis, Backend, Frontend)
docker compose up -d

# Verifique logs
docker compose logs -f backend
docker compose logs -f frontend
```

### 4. Acesse

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **pgAdmin:** http://localhost:5050 (opcional)

---

## 📦 Estrutura do Projeto

```
restaurant-analytics/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── api/         # API routes
│   │   ├── core/        # Config, DB, Cache
│   │   ├── models/      # Schemas, queries
│   │   └── services/    # Business logic
│   ├── tests/
│   └── requirements.txt
│
├── frontend/            # React + Vite frontend
│   ├── src/
│   │   ├── components/  # UI components
│   │   ├── hooks/       # Custom hooks
│   │   ├── lib/         # Utils, API client
│   │   └── store/       # State management
│   └── package.json
│
├── database/            # Schema e dados
│   ├── schema.sql
│   ├── migrations/
│   └── generate_data.py
│
├── docs/                # Documentação
│   ├── ARCHITECTURE.md
│   ├── API.md
│   └── DEPLOYMENT.md
│
├── TECH_STACK.md        # Decisões técnicas
└── docker-compose.yml
```

---

## 🛠️ Development

### Backend

```bash
cd backend

# Instale dependências
pip install -r requirements.txt

# Rode local (com hot reload)
uvicorn app.main:app --reload --port 8000

# Testes
pytest
```

### Frontend

```bash
cd frontend

# Instale dependências
npm install

# Rode local (com hot reload)
npm run dev

# Build production
npm run build
```

---

## 🧪 Testes

```bash
# Backend
cd backend
pytest --cov=app --cov-report=html

# Frontend
cd frontend
npm test
```

---

## 📊 Performance Targets

| Métrica | Target | Estratégia |
|---------|--------|-----------|
| API Response (P95) | < 500ms | Redis cache + índices |
| Dashboard Load | < 2s | Parallel requests + cache |
| Chart Render | < 100ms | React.memo + Recharts |

**Resultados atuais:** Ver [docs/PERFORMANCE.md](./docs/PERFORMANCE.md)

---

## 📖 Documentação

- [TECH_STACK.md](./TECH_STACK.md) - Decisões tecnológicas detalhadas
- [docs/ARCHITECTURE.md](./docs/ARCHITECTURE.md) - Arquitetura e design
- [docs/API.md](./docs/API.md) - API documentation
- [docs/DEPLOYMENT.md](./docs/DEPLOYMENT.md) - Deploy guide

---

## 🎯 Features Implementadas

### MVP (v1.0)
- ✅ Backend API funcionando (FastAPI)
- ✅ Conexão com PostgreSQL (500k+ vendas)
- ✅ Cache com Redis
- ✅ Frontend base (React + TailwindCSS)
- ✅ Health check endpoint

### Em Desenvolvimento
- ⏳ Dashboard com KPIs principais
- ⏳ Filtros (data, loja, canal)
- ⏳ Gráficos (vendas, produtos, tendências)
- ⏳ Tabelas interativas
- ⏳ Export de relatórios

### Futuro (v2.0)
- ⏳ Analytics customizável (drag-and-drop)
- ⏳ Comparações temporais
- ⏳ Alertas automáticos
- ⏳ Insights com IA

---

## 🚢 Deploy

### Opção 1: Docker Compose (Local/VPS)

```bash
docker compose up -d
```

### Opção 2: Railway (Recomendado)

1. Push para GitHub
2. Conecte no Railway
3. Deploy automático

### Opção 3: Render

Ver [docs/DEPLOYMENT.md](./docs/DEPLOYMENT.md)

---

## 🤝 Contribuindo

Este é um projeto individual para o Nola God Level Challenge, mas sugestões são bem-vindas!

---

## 📝 License

MIT License - ver [LICENSE](./LICENSE)

---

## 👤 Autor

**Genis Ferreira**

- GitHub: [@SEU-USUARIO](https://github.com/SEU-USUARIO)
- Email: seu-email@example.com

---

## 🙏 Agradecimentos

- **Nola/Arcca** pelo desafio incrível
- **Comunidade open-source** pelas ferramentas

---

**Desenvolvido com ❤️ para o Nola God Level Challenge • 2025**
