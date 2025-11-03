# 🏗️ TECH_STACK.md - Definição da Stack Tecnológica

## 📋 Visão Geral

Este documento detalha todas as decisões tecnológicas para a plataforma de analytics para restaurantes, com foco em **performance, escalabilidade e usabilidade**.

---

## 🎯 Requisitos Técnicos Prioritários

1. **Performance**: Queries < 1s para 500k+ registros
2. **Usabilidade**: Interface intuitiva para usuários não-técnicos
3. **Flexibilidade**: Dashboards customizáveis sem código
4. **Manutenibilidade**: Código limpo, testável e documentado
5. **Deploy**: Fácil de deployar e demonstrar

---

## 🏛️ Arquitetura Geral

```
┌─────────────────────────────────────────────────────────────┐
│                      FRONTEND LAYER                         │
│  React 18 + Vite + TanStack Query + Recharts               │
│  - Dashboard Builder                                        │
│  - Interactive Visualizations                               │
│  - Real-time Filters                                        │
└─────────────────────┬───────────────────────────────────────┘
                      │ REST API (JSON)
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                      BACKEND LAYER                          │
│  FastAPI (Python) + asyncpg + Pydantic                     │
│  - Analytics Engine                                         │
│  - Query Builder                                            │
│  - Aggregation Logic                                        │
└─────────────────────┬───────────────────────────────────────┘
                      │ SQL Queries
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                    DATABASE LAYER                           │
│  PostgreSQL 15                                              │
│  - Raw Tables (OLTP)                                        │
│  - Materialized Views (OLAP)                                │
│  - Strategic Indexes                                        │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎨 Frontend Stack

### **Core: React 18 + Vite**

**Escolha:** React 18 com Vite como bundler

**Por quê?**
- ✅ **React 18**: Concurrent rendering, Suspense para data fetching
- ✅ **Vite**: Build ultra-rápido (10x mais rápido que Webpack)
- ✅ **Ecossistema maduro**: Milhares de libraries prontas
- ✅ **TypeScript nativo**: Type safety completo

**Alternativas consideradas:**
- ❌ **Next.js**: Over-engineering para este caso (não precisamos SSR)
- ❌ **Vue/Svelte**: Menor ecossistema de visualizações

```json
{
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.3.1",
    "vite": "^5.4.0"
  }
}
```

---

### **Data Fetching: TanStack Query (React Query)**

**Escolha:** TanStack Query v5

**Por quê?**
- ✅ **Cache automático** no client-side
- ✅ **Stale-while-revalidate**: Dados instantâneos + atualização em background
- ✅ **Deduplicação**: Múltiplos componentes pedindo mesma data = 1 request
- ✅ **Retry automático** e error handling
- ✅ **DevTools** para debug

**Performance Impact:**
```typescript
// Sem cache: 10 componentes = 10 requests ao backend
// Com TanStack Query: 10 componentes = 1 request (cached)
```

```json
{
  "dependencies": {
    "@tanstack/react-query": "^5.56.0",
    "@tanstack/react-query-devtools": "^5.56.0"
  }
}
```

---

### **Visualizações: Recharts**

**Escolha:** Recharts como biblioteca principal

**Por quê?**
- ✅ **Built for React**: Componentes nativos React
- ✅ **Declarativo**: Código limpo e legível
- ✅ **Performático**: Renderiza via SVG, smooth animations
- ✅ **Responsivo**: Mobile-friendly out of the box
- ✅ **Customizável**: Controle total sobre aparência

**Tipos de gráficos suportados:**
- Line Charts (tendências temporais)
- Bar Charts (comparações)
- Pie/Donut Charts (distribuições)
- Area Charts (volumes)
- Composed Charts (múltiplas métricas)

**Alternativas:**
- ❌ **Apache ECharts**: Mais poderoso, mas menos idiomático para React
- ❌ **D3.js**: Muito low-level, curva de aprendizado alta
- ❌ **Chart.js**: Menos React-friendly

```json
{
  "dependencies": {
    "recharts": "^2.12.0"
  }
}
```

**Exemplo de código:**
```typescript
<LineChart data={salesData}>
  <CartesianGrid strokeDasharray="3 3" />
  <XAxis dataKey="date" />
  <YAxis />
  <Tooltip />
  <Legend />
  <Line type="monotone" dataKey="revenue" stroke="#8884d8" />
</LineChart>
```

---

### **Tabelas: TanStack Table**

**Escolha:** TanStack Table v8

**Por quê?**
- ✅ **Virtualização**: Renderiza apenas linhas visíveis (performance)
- ✅ **Sorting, filtering, pagination** built-in
- ✅ **Headless**: Total controle do UI
- ✅ **TypeScript-first**

```json
{
  "dependencies": {
    "@tanstack/react-table": "^8.20.0"
  }
}
```

---

### **State Management: Zustand**

**Escolha:** Zustand (estado global leve)

**Por quê?**
- ✅ **Minimalista**: ~1KB, zero boilerplate
- ✅ **Simples**: Mais fácil que Redux/Context API
- ✅ **Performance**: Re-renders otimizados

**Uso:**
- Filtros globais (date range, store, channel)
- Configuração de dashboards
- User preferences

**Alternativas:**
- ❌ **Redux Toolkit**: Over-engineering para este caso
- ❌ **Context API**: Performance issues com múltiplos consumers

```json
{
  "dependencies": {
    "zustand": "^4.5.0"
  }
}
```

---

### **UI Components: shadcn/ui + TailwindCSS**

**Escolha:** shadcn/ui (componentes) + TailwindCSS (estilização)

**Por quê?**
- ✅ **shadcn/ui**: Componentes modernos, acessíveis, copiáveis (não npm install)
- ✅ **TailwindCSS**: Utility-first, design system consistente
- ✅ **Radix UI**: Base dos componentes shadcn (acessibilidade A+)
- ✅ **Dark mode** ready

**Componentes principais:**
- Button, Card, Dialog, Dropdown, Select
- DatePicker (para filtros de data)
- Tabs, Accordion, Popover

```json
{
  "dependencies": {
    "tailwindcss": "^3.4.0",
    "@radix-ui/react-*": "^1.0.0",
    "class-variance-authority": "^0.7.0",
    "clsx": "^2.1.0",
    "tailwind-merge": "^2.2.0"
  }
}
```

---

### **Date Handling: date-fns**

**Escolha:** date-fns

**Por quê?**
- ✅ **Leve**: Tree-shakeable (só importa o que usa)
- ✅ **Moderno**: TypeScript nativo
- ✅ **Imutável**: Sem surpresas

**Alternativas:**
- ❌ **Moment.js**: Legado, pesado (67KB)
- ❌ **Day.js**: Bom, mas date-fns tem melhor TS support

```json
{
  "dependencies": {
    "date-fns": "^3.6.0"
  }
}
```

---

## ⚡ Backend Stack

### **Core: FastAPI (Python 3.11+)**

**Escolha:** FastAPI com Python 3.11+

**Por quê?**
- ✅ **Performance**: Um dos frameworks Python mais rápidos (async nativo)
- ✅ **Type Safety**: Pydantic validation automática
- ✅ **Auto-documentation**: Swagger UI e ReDoc out of the box
- ✅ **Async/await**: Queries paralelas, não-bloqueante
- ✅ **Data Science**: Pandas/Polars para transformações complexas

**Performance Comparison:**
```
FastAPI (async): ~10,000 req/s
Django: ~1,000 req/s
Flask: ~2,000 req/s
Node.js (Express): ~15,000 req/s
```

**FastAPI é ideal porque:**
- Performance próxima do Node.js
- Melhor para data manipulation (Python >>> JavaScript para analytics)
- Type safety via Pydantic

**Alternativas:**
- ❌ **Node.js (NestJS)**: Bom, mas Python é melhor para data analytics
- ❌ **Django**: Muito pesado e lento para APIs
- ❌ **Flask**: Sem async nativo

```txt
fastapi==0.115.0
uvicorn[standard]==0.30.0  # ASGI server production-ready
```

---

### **Database Driver: asyncpg**

**Escolha:** asyncpg (PostgreSQL async driver)

**Por quê?**
- ✅ **Fastest**: 3x mais rápido que psycopg2
- ✅ **Async nativo**: Non-blocking queries
- ✅ **Connection pooling**: Reutiliza conexões

**Performance:**
```python
# Query pesada (100k registros)
psycopg2 (sync): ~3.2s
asyncpg: ~0.9s
```

```txt
asyncpg==0.29.0
```

---

### **Validation: Pydantic V2**

**Escolha:** Pydantic V2

**Por quê?**
- ✅ **Type safety**: Validação automática de requests/responses
- ✅ **Performance**: V2 é 5-50x mais rápido (Rust core)
- ✅ **Auto-serialization**: JSON nativo

**Exemplo:**
```python
from pydantic import BaseModel
from datetime import date

class SalesQuery(BaseModel):
    start_date: date
    end_date: date
    store_ids: list[int] | None = None
    channel_ids: list[int] | None = None
    
# FastAPI valida automaticamente!
```

```txt
pydantic==2.9.0
pydantic-settings==2.5.0
```

---

### **Data Manipulation: Polars**

**Escolha:** Polars (não Pandas)

**Por quê?**
- ✅ **Performance**: 10-100x mais rápido que Pandas
- ✅ **Lazy evaluation**: Otimiza queries automaticamente
- ✅ **Rust-based**: Zero-copy, memory efficient
- ✅ **Sintaxe moderna**: Mais limpa que Pandas

**Benchmark (agregação 1M rows):**
```
Pandas: 2.5s
Polars (lazy): 0.3s
```

**Uso:**
- Transformações complexas pós-query
- Agregações customizadas
- Cálculos de métricas (RFM, cohorts)

**Alternativa:**
- Pandas: Se precisar de libs que dependem dele

```txt
polars==1.9.0
```

---

### **HTTP Client (optional): httpx**

Para integrações futuras (webhooks, APIs externas)

```txt
httpx==0.27.0
```

---

## 🗄️ Database Stack

### **Core: PostgreSQL 15**

**Escolha:** PostgreSQL 15

**Por quê?**
- ✅ **JSONB**: Para metadata flexível
- ✅ **Window functions**: Agregações complexas
- ✅ **CTEs**: Queries legíveis e performáticas
- ✅ **Materialized Views**: Pré-agregações
- ✅ **Partitioning**: Escala futura por data

**Alternativas consideradas:**
- ❌ **ClickHouse**: Over-engineering, complexo demais
- ❌ **TimescaleDB**: Bom, mas não necessário ainda
- ❌ **MySQL**: Sem JSONB, window functions limitadas

---

### **Optimization Strategy**

**1. Índices Estratégicos**
```sql
-- Queries temporais (BRIN = Block Range Index)
CREATE INDEX idx_sales_created_at_brin ON sales USING BRIN(created_at);

-- Filtros comuns
CREATE INDEX idx_sales_store_channel_date 
ON sales(store_id, channel_id, created_at DESC, sale_status_desc);

-- Produtos
CREATE INDEX idx_product_sales_product_id ON product_sales(product_id);
CREATE INDEX idx_product_sales_sale_id ON product_sales(sale_id);

-- GIN index para full-text search (futuro)
CREATE INDEX idx_products_name_gin ON products USING GIN(to_tsvector('portuguese', name));
```

**2. Materialized Views**
```sql
-- Vendas agregadas por dia/hora/loja/canal
CREATE MATERIALIZED VIEW mv_sales_hourly AS
SELECT 
  DATE_TRUNC('hour', created_at) as hour,
  store_id, channel_id,
  COUNT(*) as total_sales,
  SUM(total_amount) as revenue,
  AVG(total_amount) as avg_ticket,
  PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY total_amount) as median_ticket
FROM sales
WHERE sale_status_desc = 'COMPLETED'
GROUP BY 1, 2, 3;

CREATE INDEX ON mv_sales_hourly(hour, store_id, channel_id);

-- Refresh estratégia
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_sales_hourly;
```

**3. Query Optimization**
```sql
-- Use EXPLAIN ANALYZE em todas queries
EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) 
SELECT ...;

-- VACUUM e ANALYZE regulares
VACUUM ANALYZE sales;
```

---

## 🐳 DevOps Stack

### **Containerization: Docker + Docker Compose**

**Setup:**
```yaml
services:
  postgres:
    image: postgres:15-alpine
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      POSTGRES_DB: restaurant_analytics
      POSTGRES_USER: analytics
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U analytics"]
      interval: 5s
      
  backend:
    build: ./backend
    depends_on:
      postgres:
        condition: service_healthy
    environment:
      DATABASE_URL: postgresql+asyncpg://analytics:${DB_PASSWORD}@postgres/restaurant_analytics
      
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
```

---

### **Deploy: Railway / Render**

**Opção 1: Railway** (Recomendado)
- ✅ Deploy automático via GitHub
- ✅ PostgreSQL managed
- ✅ Free tier generoso
- ✅ Logs e monitoring built-in

**Opção 2: Render**
- ✅ Free tier para demos
- ✅ Auto-deploy do GitHub
- ✅ SSL gratuito

**Opção 3: Vercel (Frontend) + Railway (Backend + DB)**
- ✅ Frontend ultra-rápido (Edge CDN)
- ✅ Backend separado

---

### **CI/CD: GitHub Actions**

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run backend tests
        run: |
          cd backend
          pip install -r requirements.txt
          pytest
      
      - name: Run frontend tests
        run: |
          cd frontend
          npm install
          npm test
  
  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to Railway
        uses: railway/deploy@v1
```

---

## 📦 Estrutura do Projeto

```
restaurant-analytics/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── routes/
│   │   │   │   ├── analytics.py
│   │   │   │   ├── sales.py
│   │   │   │   └── products.py
│   │   │   └── dependencies.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   └── database.py
│   │   ├── models/
│   │   │   ├── schemas.py
│   │   │   └── queries.py
│   │   ├── services/
│   │   │   ├── analytics_engine.py
│   │   │   └── query_builder.py
│   │   └── main.py
│   ├── tests/
│   ├── requirements.txt
│   ├── Dockerfile
│   └── pytest.ini
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── charts/
│   │   │   ├── dashboard/
│   │   │   ├── filters/
│   │   │   └── ui/
│   │   ├── hooks/
│   │   ├── lib/
│   │   │   ├── api.ts
│   │   │   └── utils.ts
│   │   ├── store/
│   │   ├── types/
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── public/
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   └── Dockerfile
│
├── database/
│   ├── schema.sql
│   ├── migrations/
│   ├── seeds/
│   └── generate_data.py
│
├── docs/
│   ├── ARCHITECTURE.md
│   ├── API.md
│   └── DEPLOYMENT.md
│
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
```

---

## 🧪 Testing Stack

### **Backend:**
```txt
pytest==8.3.0
pytest-asyncio==0.24.0
pytest-cov==5.0.0
httpx==0.27.0  # For API testing
faker==30.0.0  # Test data generation
```

### **Frontend:**
```json
{
  "devDependencies": {
    "vitest": "^2.1.0",
    "@testing-library/react": "^16.0.0",
    "@testing-library/jest-dom": "^6.5.0",
    "@testing-library/user-event": "^14.5.0"
  }
}
```

---

## 🎯 Performance Targets

| Métrica | Target | Estratégia |
|---------|--------|-----------|
| API Response (P50) | < 200ms | Índices PostgreSQL + TanStack Query cache |
| API Response (P95) | < 500ms | Materialized views + query optimization |
| API Response (P99) | < 1s | Query optimization |
| Frontend FCP | < 1.5s | Code splitting |
| Frontend TTI | < 3s | Lazy loading |
| Dashboard Load | < 2s | Parallel requests |
| Chart Render | < 100ms | Recharts + React.memo |

---

## 📊 Stack Summary

| Layer | Technology | Justification |
|-------|-----------|---------------|
| **Frontend** | React 18 + Vite | Modern, fast, ecosystem |
| **Data Fetching** | TanStack Query | Cache + performance |
| **Charts** | Recharts | React-native, declarative |
| **UI** | shadcn/ui + Tailwind | Modern, accessible |
| **State** | Zustand | Simple, performant |
| **Backend** | FastAPI | Fast, async, type-safe |
| **DB Driver** | asyncpg | 3x faster than psycopg2 |
| **Data Processing** | Polars | 10-100x faster than Pandas |
| **Database** | PostgreSQL 15 | Robust, feature-rich |
| **Client Cache** | TanStack Query | Client-side caching |
| **Deploy** | Railway/Render | Easy, free tier |

---

**Documento criado em:** 29/10/2025  
**Autor:** Genis Ferreira (God Level Challenge)  
**Versão:** 1.0
