# 🏗️ Arquitetura da Solução

## Visão Geral

Esta é a documentação detalhada da arquitetura da **Restaurant Analytics Platform**, desenvolvida para o Nola God Level Challenge.

## Decisões Arquiteturais

### 1. **Arquitetura em Camadas**

Optamos por uma arquitetura em camadas (layered architecture) com separação clara de responsabilidades:

```
Frontend (React) ←→ Backend (FastAPI) ←→ Database (PostgreSQL)
```

**Justificativa:**
- ✅ Separação de concerns
- ✅ Facilita testes e manutenção
- ✅ Permite escalar cada camada independentemente
- ✅ Time-to-market rápido

**Alternativas consideradas:**
- ❌ **Microserviços**: Over-engineering para o escopo atual
- ❌ **Serverless**: Complexidade adicional de infraestrutura
- ❌ **Monolito Full-Stack**: Menor flexibilidade de deploy

---

### 2. **Backend: FastAPI (Python)**

**Por quê FastAPI?**
- Performance próxima do Node.js (~10k req/s)
- Async/await nativo (non-blocking I/O)
- Type safety com Pydantic
- Auto-documentação (Swagger/OpenAPI)
- Python é superior para data analytics

**Trade-offs:**
- ➕ Excelente para manipulação de dados
- ➕ Ecossistema rico (Pandas, Polars, NumPy)
- ➖ Ligeiramente mais lento que Go/Rust (mas suficiente)

---

### 3. **Database: PostgreSQL 15**

**Por quê PostgreSQL?**
- JSONB para metadata flexível
- Window functions para agregações complexas
- Materialized Views para pré-agregações
- Excelente performance com índices corretos

**Estratégia de Otimização:**
- Índices compostos em colunas filtradas frequentemente
- BRIN index para queries temporais
- Materialized Views para agregações pesadas
- Connection pooling (asyncpg)

**Trade-offs:**
- ➕ Feature-rich, maduro, confiável
- ➕ Suporte nativo a analytics (window functions, CTEs)
- ➖ Não é um OLAP database (mas suficiente para 500k vendas)

**Alternativas consideradas:**
- ❌ **ClickHouse**: Over-engineering, complexo demais
- ❌ **TimescaleDB**: Não necessário ainda
- ❌ **MongoDB**: Não ideal para analytics estruturado

---

### 4. **Frontend: React + Vite**

**Por quê React?**
- Ecossistema maduro
- Biblioteca de componentes rica (Recharts, TanStack)
- Performance excelente com Vite

**Por quê Vite (não Webpack/CRA)?**
- Build 10-100x mais rápido
- HMR (Hot Module Replacement) instantâneo
- Moderna arquitetura ESM

**Trade-offs:**
- ➕ Developer Experience excelente
- ➕ Time-to-market rápido
- ➖ Bundle size maior que Svelte (mas aceitável)

---

### 5. **Data Fetching: TanStack Query**

**Por quê TanStack Query?**
- Cache automático no client-side
- Deduplicação de requests
- Stale-while-revalidate pattern
- Retry e error handling built-in

**Impacto na Performance:**
```typescript
// Sem cache: 10 componentes = 10 requests
// Com TanStack Query: 10 componentes = 1 request (cached)
```

---

### 6. **Charts: Recharts**

**Por quê Recharts?**
- Componentes declarativos nativos React
- Performance excelente (SVG)
- Customização total
- Responsivo out-of-the-box

**Alternativas consideradas:**
- ❌ **ECharts**: Menos idiomático para React
- ❌ **D3.js**: Muito low-level, curva de aprendizado alta

---

## Fluxo de Dados

### Query para Dashboard

```
1. User seleciona filtros (data, loja, canal)
   ↓
2. Frontend → TanStack Query verifica cache local
   ↓ (cache miss)
3. Request HTTP → Backend FastAPI
   ↓
4. Backend → SQL query otimizada (asyncpg)
   ↓
5. PostgreSQL → Usa índices + materialized views
   ↓
6. Resultado → Backend processa com Polars (se necessário)
   ↓
7. Response JSON → Frontend
   ↓
8. TanStack Query → Cache local + render
   ↓
9. Recharts → Renderiza visualização
```

**Tempo total (P95):**
- Cache hit (TanStack Query): ~5ms
- Cache miss: ~300-500ms (depende da complexidade da query)

---

## Estratégia de Performance

### Backend

1. **Connection Pooling**: asyncpg pool (10 conexões)
2. **Query Optimization**: EXPLAIN ANALYZE em todas queries
3. **Async I/O**: Non-blocking queries paralelas
4. **Data Processing**: Polars para transformações (10-100x mais rápido que Pandas)

### Database

1. **Índices Estratégicos**:
```sql
CREATE INDEX idx_sales_created_at_brin ON sales USING BRIN(created_at);
CREATE INDEX idx_sales_filters ON sales(store_id, channel_id, sale_status_desc);
```

2. **Materialized Views**:
```sql
CREATE MATERIALIZED VIEW mv_sales_hourly AS
SELECT DATE_TRUNC('hour', created_at), store_id, channel_id,
       COUNT(*), SUM(total_amount), AVG(total_amount)
FROM sales WHERE sale_status_desc = 'COMPLETED'
GROUP BY 1, 2, 3;
```

3. **VACUUM e ANALYZE** regulares

### Frontend

1. **Code Splitting**: Lazy loading de rotas
2. **React.memo**: Previne re-renders desnecessários
3. **Virtual Scrolling**: TanStack Table para grandes listas
4. **Image Optimization**: WebP + lazy loading

---

## Escalabilidade

### Vertical Scaling (Curto Prazo)

- PostgreSQL: ↑ RAM, ↑ CPU cores
- Backend: ↑ workers uvicorn

### Horizontal Scaling (Longo Prazo)

- Backend: Load balancer + múltiplas instâncias
- Database: Read replicas para queries analíticas
- Frontend: CDN (Vercel/Cloudflare)
- Cache: Considerar Redis ou cache HTTP para queries repetidas

---

## Segurança

1. **Environment Variables**: Secrets em .env (não commitado)
2. **CORS**: Whitelist de origins permitidas
3. **SQL Injection**: Parametrized queries (asyncpg)
4. **Rate Limiting**: (futuro) Limitação de requests por IP

---

## Monitoramento (Futuro)

1. **APM**: Sentry para error tracking
2. **Metrics**: Prometheus + Grafana
3. **Logs**: Estruturados (JSON) + ELK Stack
4. **Uptime**: UptimeRobot ou Pingdom

---

## Deploy

### Desenvolvimento
```bash
docker compose up
```

### Produção

**Opção 1: Railway** (Recomendado)
- Backend + PostgreSQL em Railway
- Frontend em Vercel

**Opção 2: Render**
- Tudo em Render (free tier)

**Opção 3: VPS**
- Docker Compose em VPS (DigitalOcean, Linode)
- Nginx reverse proxy
- Let's Encrypt SSL

---

## Próximos Passos

1. ✅ MVP: Dashboard básico funcionando
2. ⏳ Features avançadas: Filtros customizáveis, comparações
3. ⏳ Testes: Unit + Integration + E2E
4. ⏳ Deploy: Produção em Railway
5. ⏳ Monitoramento: Sentry + logs

---

**Documento atualizado em:** 29/10/2025

