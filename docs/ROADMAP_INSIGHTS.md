# 🎯 ROADMAP: Analytics com Insights Automáticos
> **Objetivo:** Transformar dados em decisões acionáveis para gerar mais lucro

**Última atualização:** 30/10/2025  
**Status Atual:** ✅ Backend de Insights implementado | ⏳ Frontend parcialmente implementado  
**Próximo Passo:** Finalizar integração frontend e avançar para Sprint 2

---

## 📊 Visão Geral

### Proposta de Valor
**Antes:** "Aqui estão seus dados, interprete você mesmo"  
**Depois:** "⚠️ Você está perdendo R$ 12.400/mês. Veja como resolver →"

### Entregas por Sprint
| Sprint | Foco | Valor Gerado | Tempo |
|--------|------|--------------|-------|
| **Sprint 1** | Insights Automáticos Core | Maria vê problemas/oportunidades ao abrir sistema | 5 dias |
| **Sprint 2** | Insights Avançados + Exportação | Decisões baseadas em previsões + relatórios para sócio | 5 dias |
| **Sprint 3** | Templates por Persona + Favoritos | Cada usuário vê o que importa para seu papel | 3-4 dias |

**Total:** 13-14 dias úteis

---

## 🚀 SPRINT 1: Insights Automáticos Core (5 dias)

### 🎯 Objetivo
Maria abre o dashboard e vê **3-5 insights críticos** com ações claras.

### 📦 Entregas

#### **1.1 Componente Visual de Insights** ⏳ PARCIALMENTE IMPLEMENTADO
**Arquivo:** `frontend/src/components/insights/InsightsPanel.tsx` (existe)

**Status:**
- ✅ Arquivo criado
- ⏳ Verificar se está integrado ao Dashboard
- ⏳ Verificar se todas as funcionalidades estão implementadas:
  - [ ] Card destacado no topo do Dashboard Geral
  - [ ] Exibir 3-5 insights mais relevantes
  - [ ] Ícones por prioridade implementados
  - [ ] Estados de loading e vazio

**Exemplo de UI:**
```
┌─────────────────────────────────────────────────────────────┐
│ 🔍 Insights Automáticos                    🔄 Atualizado há 5min │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ 🔴 CRÍTICO: Perda de R$ 12.400/mês                         │
│    340 pedidos cancelados após 35min de espera             │
│    Concentrado: Sexta/Sábado, Loja Centro, iFood           │
│    💡 Ação: Adicionar 2 entregadores nos fins de semana    │
│    [Ver Análise de Delivery →]                             │
│                                                             │
│ 🟡 OPORTUNIDADE: Item "X-Bacon Premium"                    │
│    Margem 68% mas apenas 12 vendas/dia no delivery         │
│    💡 Ação: Criar combo delivery "Premium Night"           │
│    [Ver Produtos por Contexto →]                           │
│                                                             │
│ 🟢 BOA PERFORMANCE: Loja Shopping                          │
│    +23% vendas vs mês anterior                             │
│    Destaque: Vendas no balcão cresceram 40%                │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Componentes auxiliares:**
- [ ] `InsightCard.tsx` (card individual)
- [ ] `InsightIcon.tsx` (ícone por tipo/prioridade)
- [ ] Types: `Insight`, `InsightPriority`, `InsightType`

---

#### **1.2 Backend - Endpoint de Insights** ✅ IMPLEMENTADO
**Arquivo:** `backend/app/api/routes/insights.py`

**Status:** ✅ Endpoint criado e funcionando
- ✅ Rota registrada em `main.py`
- ✅ Endpoint: `GET /api/v1/analytics/insights/automatic`
- ✅ Parâmetros: `start_date`, `end_date`, `brand_id`, `store_ids`, `limit`
- ✅ Engine de insights implementado em `backend/app/services/insights/engine.py`
- ✅ Detectores implementados:
  - ✅ `CancellationDetector` - Detecção de problemas de cancelamento
  - ✅ `ProductOpportunityDetector` - Oportunidades de produtos
  - ✅ `ChurnRiskDetector` - Risco de churn de clientes
  - ✅ `StoreOutlierDetector` - Performance de lojas (outliers)

**Response Schema:**
```python
{
  "insights": [
    {
      "id": "delivery_cancellation_spike",
      "type": "performance_issue",
      "priority": "critical",
      "title": "Alto índice de cancelamentos no delivery",
      "description": "340 pedidos cancelados após 35min de espera",
      "impact": {
        "metric": "revenue_loss",
        "value": 12400.00,
        "currency": "BRL",
        "period": "monthly"
      },
      "context": {
        "affected_stores": [1, 2],
        "affected_channels": [3],
        "affected_days": ["friday", "saturday"],
        "affected_hours": [19, 20, 21]
      },
      "recommendation": {
        "action": "Adicionar 2 entregadores nos fins de semana",
        "estimated_roi": 8500.00,
        "link_to": "/advanced?tab=delivery"
      },
      "detected_at": "2025-10-30T10:30:00Z"
    }
  ],
  "total": 3,
  "generated_at": "2025-10-30T10:30:00Z",
  "period": {
    "start_date": "2025-05-01",
    "end_date": "2025-05-31"
  }
}
```

**Schemas:**
- ✅ `InsightImpact`, `InsightContext`, `InsightRecommendation` (implementados)
- ✅ `Insight` e `InsightsResponse` (implementados em `schemas.py`)

---

#### **1.3 Service - Engine de Detecção de Insights** ✅ IMPLEMENTADO
**Arquivo:** `backend/app/services/insights/engine.py`

**Status:** ✅ Engine completo implementado
- ✅ Classe `InsightsEngine` criada
- ✅ Método `generate_insights()` implementado
- ✅ Sistema de priorização funcionando

**Métodos implementados:**
- ✅ `generate_insights()` - Orquestra detectores e prioriza resultados
- ✅ Detectores individuais implementados como classes separadas:
  - ✅ `CancellationDetector` - Detecta problemas de cancelamento/delivery
  - ✅ `ProductOpportunityDetector` - Detecta oportunidades de produtos
  - ✅ `ChurnRiskDetector` - Detecta risco de churn
  - ✅ `StoreOutlierDetector` - Detecta outliers de performance

**Lógica de Detecção (MVP):**

##### **A) Problemas de Delivery**
```sql
-- Detectar: Taxa de cancelamento > 10% OU tempo médio > 35min
SELECT 
  COUNT(*) FILTER (WHERE sale_status_desc = 'CANCELLED') * 100.0 / COUNT(*) as cancel_rate,
  AVG(EXTRACT(EPOCH FROM (delivered_at - created_at))/60) as avg_delivery_min,
  store_id, channel_id, 
  EXTRACT(DOW FROM created_at) as weekday,
  EXTRACT(HOUR FROM created_at) as hour
FROM sales s
INNER JOIN stores st ON s.store_id = st.id
WHERE st.brand_id = $1 
  AND created_at BETWEEN $2 AND $3
  AND sale_type = 'delivery'
GROUP BY store_id, channel_id, weekday, hour
HAVING COUNT(*) > 20 -- Apenas contextos com volume significativo
  AND (
    COUNT(*) FILTER (WHERE sale_status_desc = 'CANCELLED') * 100.0 / COUNT(*) > 10
    OR AVG(EXTRACT(EPOCH FROM (delivered_at - created_at))/60) > 35
  )
ORDER BY cancel_rate DESC
LIMIT 1;
```

**Se detectado:** Gerar insight tipo `performance_issue` com prioridade `critical`

##### **B) Produtos com Oportunidade**
```sql
-- Detectar: Alta margem (>60%) + Baixa venda (<20/dia) + Nunca no top 10
WITH product_stats AS (
  SELECT 
    p.id,
    p.name,
    p.price,
    p.cost,
    ((p.price - p.cost) / p.price * 100) as margin_pct,
    COUNT(ps.id) / DATE_PART('day', $3::date - $2::date) as avg_daily_sales
  FROM products p
  INNER JOIN product_sales ps ON ps.product_id = p.id
  INNER JOIN sales s ON ps.sale_id = s.id
  INNER JOIN stores st ON s.store_id = st.id
  WHERE st.brand_id = $1
    AND s.created_at BETWEEN $2 AND $3
  GROUP BY p.id
)
SELECT * FROM product_stats
WHERE margin_pct > 60 
  AND avg_daily_sales < 20
ORDER BY margin_pct DESC
LIMIT 1;
```

**Se detectado:** Gerar insight tipo `opportunity` com prioridade `attention`

##### **C) Clientes VIP em Risco**
```sql
-- Detectar: Clientes com LTV > R$ 1000/ano inativos há 30+ dias
WITH customer_value AS (
  SELECT 
    c.id,
    c.name,
    SUM(s.total_price) as ltv,
    MAX(s.created_at) as last_purchase,
    COUNT(s.id) as total_purchases
  FROM customers c
  INNER JOIN sales s ON s.customer_id = c.id
  INNER JOIN stores st ON s.store_id = st.id
  WHERE st.brand_id = $1
    AND s.created_at >= $2 - INTERVAL '12 months' -- LTV anual
  GROUP BY c.id
)
SELECT 
  COUNT(*) as at_risk_count,
  SUM(ltv) as revenue_at_risk
FROM customer_value
WHERE ltv > 1000
  AND last_purchase < CURRENT_DATE - INTERVAL '30 days'
  AND total_purchases >= 5; -- Apenas clientes recorrentes
```

**Se detectado:** Gerar insight tipo `churn_risk` com prioridade `critical`

##### **D) Performance de Lojas (Outliers)**
```sql
-- Detectar: Loja com performance 30%+ acima/abaixo da média
WITH store_performance AS (
  SELECT 
    st.id,
    st.name,
    SUM(s.total_price) as revenue,
    COUNT(s.id) as orders,
    AVG(s.total_price) as avg_ticket
  FROM stores st
  LEFT JOIN sales s ON s.store_id = st.id 
    AND s.created_at BETWEEN $2 AND $3
  WHERE st.brand_id = $1
  GROUP BY st.id
),
avg_metrics AS (
  SELECT 
    AVG(revenue) as avg_revenue,
    AVG(orders) as avg_orders,
    AVG(avg_ticket) as avg_ticket
  FROM store_performance
)
SELECT 
  sp.*,
  (sp.revenue - am.avg_revenue) / am.avg_revenue * 100 as revenue_diff_pct
FROM store_performance sp, avg_metrics am
WHERE ABS((sp.revenue - am.avg_revenue) / am.avg_revenue * 100) > 30
ORDER BY ABS(revenue_diff_pct) DESC;
```

**Se detectado:** Gerar insight tipo `performance_alert` (positivo ou negativo)

##### **E) Anomalias de Receita**
```sql
-- Detectar: Queda >15% vs período anterior
WITH current_period AS (
  SELECT SUM(total_price) as revenue
  FROM sales s
  INNER JOIN stores st ON s.store_id = st.id
  WHERE st.brand_id = $1
    AND s.created_at BETWEEN $2 AND $3
),
previous_period AS (
  SELECT SUM(total_price) as revenue
  FROM sales s
  INNER JOIN stores st ON s.store_id = st.id
  WHERE st.brand_id = $1
    AND s.created_at BETWEEN 
      $2 - ($3::date - $2::date) AND $2
)
SELECT 
  cp.revenue as current_revenue,
  pp.revenue as previous_revenue,
  ((cp.revenue - pp.revenue) / pp.revenue * 100) as change_pct
FROM current_period cp, previous_period pp
WHERE ABS((cp.revenue - pp.revenue) / pp.revenue * 100) > 15;
```

**Se detectado:** Gerar insight tipo `revenue_anomaly`

**Priorização:**
1. Ordenar por `priority` (critical > attention > positive)
2. Dentro de cada prioridade, ordenar por `impact.value` (maior primeiro)
3. Retornar top N (default: 5)

---

#### **1.4 Integração no Dashboard Geral** (0,5 dia)
**Arquivo:** `frontend/src/components/dashboard/Dashboard.tsx`

**Mudanças:**
- [ ] Importar `InsightsPanel`
- [ ] Adicionar query para buscar insights:
```typescript
const { data: insights } = useQuery({
  queryKey: ['insights', dateRange, brandId],
  queryFn: () => fetchApi('/insights/automatic', {
    start_date: dateRange.startDate,
    end_date: dateRange.endDate,
    store_ids: dateRange.storeIds,
    limit: 5
  }),
  enabled: !!brandId,
  refetchInterval: 5 * 60 * 1000 // Atualizar a cada 5min
})
```
- [ ] Renderizar `<InsightsPanel insights={insights} />` logo após filtros

---

#### **1.5 Filtro de Canal (da Sprint Original)** (0,5 dia)
**Arquivo:** `frontend/src/components/filters/ChannelFilter.tsx` (já existe, melhorar)

**Melhorias:**
- [ ] Buscar canais dinamicamente do backend (`/channels/list?brand_id=X`)
- [ ] Integrar no `Dashboard.tsx` e `AdvancedDashboard.tsx`
- [ ] Adicionar `channelIds` ao `dateRange` state

---

#### **1.6 Comparação de Lojas Lado a Lado** (0,5 dia)
**Arquivo:** `frontend/src/components/dashboard/StoreComparisonView.tsx` (criar)

**Funcionalidade:**
- [ ] Modal ou seção expansível
- [ ] Selecionar 2 lojas para comparar
- [ ] Exibir métricas lado a lado:
  - Receita total
  - Ticket médio
  - Total de pedidos
  - Taxa de cancelamento
  - Avaliação média (se disponível)
- [ ] Destacar diferenças significativas (>20%)

**Integração:**
- [ ] Botão no `Dashboard.tsx`: "Comparar Lojas"
- [ ] Reutilizar endpoint `/stores` existente

---

### ✅ Checklist de Conclusão - Sprint 1

**Backend:** ✅ COMPLETO
- [x] Arquivo `insights.py` criado com endpoint `/insights/automatic`
- [x] Engine de insights criado com detectores implementados
- [x] Schemas adicionados em `schemas.py`
- [ ] Testes básicos (manual via curl/Postman) - **PENDENTE**

**Frontend:** ⏳ PARCIAL
- [x] Componente `InsightsPanel.tsx` criado
- [ ] Integração completa ao Dashboard - **VERIFICAR**
- [ ] `ChannelFilter.tsx` melhorado e integrado - **VERIFICAR**
- [ ] `StoreComparisonView.tsx` criado - **PENDENTE**
- [ ] Tipos TypeScript atualizados - **VERIFICAR**

**Validação:**
- [ ] Maria abre dashboard e vê 3-5 insights relevantes
- [ ] Insights refletem dados reais do período selecionado
- [ ] Links "Ver Detalhes" navegam para seção correta
- [ ] Filtro de canal funciona em ambos os dashboards
- [ ] Comparação de 2 lojas exibe métricas corretas

---

## 📊 SPRINT 2: Insights Avançados + Exportação (5 dias)

### 🎯 Objetivo
Insights mais profundos (padrões, previsões) + relatório executivo para apresentar ao sócio.

### 📦 Entregas

#### **2.1 Insights de Contexto/Padrões** (2 dias)

##### **A) Detector de Padrões Temporais**
**Método:** `InsightsEngine.detect_temporal_patterns()`

**Exemplos:**
- "Toda segunda-feira há queda de 30% nas vendas"
- "Vendas no delivery crescem 40% após 21h"
- "Produto X vende 5x mais aos sábados"

**Query base:**
```sql
-- Detectar: Dia da semana com performance consistentemente diferente
WITH daily_performance AS (
  SELECT 
    EXTRACT(DOW FROM created_at) as weekday,
    DATE_TRUNC('week', created_at) as week,
    SUM(total_price) as revenue
  FROM sales s
  INNER JOIN stores st ON s.store_id = st.id
  WHERE st.brand_id = $1
    AND created_at BETWEEN $2 AND $3
  GROUP BY weekday, week
)
SELECT 
  weekday,
  AVG(revenue) as avg_revenue,
  STDDEV(revenue) as stddev,
  (AVG(revenue) - overall.avg) / overall.avg * 100 as diff_from_avg_pct
FROM daily_performance,
  (SELECT AVG(revenue) as avg FROM daily_performance) overall
GROUP BY weekday, overall.avg
HAVING ABS((AVG(revenue) - overall.avg) / overall.avg * 100) > 20
  AND COUNT(*) >= 4 -- Pelo menos 4 semanas de dados
ORDER BY ABS(diff_from_avg_pct) DESC;
```

##### **B) Detector de Correlações**
**Método:** `InsightsEngine.detect_correlations()`

**Exemplos:**
- "Quando vende Refrigerante, vende Batata Frita em 80% dos casos"
- "Canal iFood + Sexta à noite = 65% de pedidos premium"

**Query base:**
```sql
-- Detectar: Produtos frequentemente comprados juntos
WITH product_pairs AS (
  SELECT 
    ps1.product_id as product_a,
    ps2.product_id as product_b,
    COUNT(DISTINCT ps1.sale_id) as together_count
  FROM product_sales ps1
  INNER JOIN product_sales ps2 ON ps1.sale_id = ps2.sale_id
  INNER JOIN sales s ON ps1.sale_id = s.id
  INNER JOIN stores st ON s.store_id = st.id
  WHERE st.brand_id = $1
    AND ps1.product_id < ps2.product_id -- Evitar duplicatas
    AND s.created_at BETWEEN $2 AND $3
  GROUP BY ps1.product_id, ps2.product_id
),
product_totals AS (
  SELECT 
    product_id,
    COUNT(DISTINCT sale_id) as total_sales
  FROM product_sales ps
  INNER JOIN sales s ON ps.sale_id = s.id
  INNER JOIN stores st ON s.store_id = st.id
  WHERE st.brand_id = $1
    AND s.created_at BETWEEN $2 AND $3
  GROUP BY product_id
)
SELECT 
  pp.product_a,
  pp.product_b,
  pp.together_count,
  pt.total_sales as product_a_total,
  (pp.together_count::float / pt.total_sales * 100) as correlation_pct
FROM product_pairs pp
INNER JOIN product_totals pt ON pp.product_a = pt.product_id
WHERE pp.together_count::float / pt.total_sales > 0.6 -- Correlação > 60%
  AND pp.together_count > 20 -- Mínimo 20 ocorrências
ORDER BY correlation_pct DESC
LIMIT 5;
```

---

#### **2.2 Insights Preditivos Simples** (2 dias)

##### **A) Previsão de Demanda (Próximos 7 dias)**
**Método:** `InsightsEngine.predict_demand()`

**Algoritmo:** Média móvel ponderada + ajuste sazonal

```python
# Pseudocódigo
def predict_demand(self, product_id: int, days_ahead: int = 7):
    # 1. Buscar vendas dos últimos 28 dias
    historical_sales = self.get_product_sales_last_n_days(product_id, 28)
    
    # 2. Calcular média móvel ponderada (últimos 7 dias pesam mais)
    weights = [1, 1, 1, 1.2, 1.2, 1.5, 1.5]  # Últimos dias pesam mais
    weighted_avg = sum(sales[-7:] * weights) / sum(weights)
    
    # 3. Ajustar por dia da semana (ex: sábado vende 1.4x mais)
    weekday_factors = self.get_weekday_factors(product_id)
    
    # 4. Gerar previsões
    predictions = []
    for day in range(days_ahead):
        weekday = (current_weekday + day) % 7
        predicted = weighted_avg * weekday_factors[weekday]
        predictions.append({
            'date': current_date + timedelta(days=day),
            'predicted_sales': round(predicted),
            'confidence': 'medium'  # low/medium/high baseado em stddev
        })
    
    return predictions
```

**Insight gerado:**
```json
{
  "type": "demand_forecast",
  "priority": "attention",
  "title": "Pico de demanda previsto para Sábado",
  "description": "Produto 'X-Bacon' terá demanda 40% acima da média",
  "recommendation": {
    "action": "Garantir +15kg de carne em estoque",
    "estimated_impact": "Evitar perda de R$ 2.300 em vendas"
  }
}
```

##### **B) Alerta de Churn Iminente**
**Método:** `InsightsEngine.predict_churn_risk()`

**Lógica:**
```sql
-- Clientes que ESTÃO PRESTES a entrar em churn (15-25 dias sem comprar)
-- Ainda dá tempo de recuperar!
WITH customer_activity AS (
  SELECT 
    c.id,
    c.name,
    MAX(s.created_at) as last_purchase,
    CURRENT_DATE - MAX(s.created_at)::date as days_inactive,
    COUNT(s.id) as total_purchases,
    SUM(s.total_price) as ltv
  FROM customers c
  INNER JOIN sales s ON s.customer_id = c.id
  INNER JOIN stores st ON s.store_id = st.id
  WHERE st.brand_id = $1
    AND s.created_at >= CURRENT_DATE - INTERVAL '6 months'
  GROUP BY c.id
)
SELECT 
  COUNT(*) as at_risk_count,
  SUM(ltv) as revenue_at_risk
FROM customer_activity
WHERE days_inactive BETWEEN 15 AND 25  -- "Zona de perigo"
  AND total_purchases >= 3
  AND ltv > 500;
```

**Insight gerado:**
```json
{
  "type": "churn_prevention",
  "priority": "critical",
  "title": "12 clientes prestes a entrar em churn",
  "description": "R$ 8.400 em risco nos próximos 10 dias",
  "recommendation": {
    "action": "Enviar cupom 15% OFF 'Sentimos sua Falta'",
    "estimated_roi": "Recuperar ~40% = R$ 3.360"
  }
}
```

---

#### **2.3 Exportação Inteligente de Relatórios** (1 dia)

##### **Componente:** `ExportButton.tsx` (melhorar o existente)

**Funcionalidades:**
- [ ] Exportar para PDF ou Excel
- [ ] Incluir insights automáticos no topo
- [ ] Narrativa automática ("Story" dos dados)
- [ ] Gráficos principais
- [ ] Formatação profissional

**Backend:**
**Endpoint:** `POST /api/v1/analytics/export/report`

**Request:**
```json
{
  "format": "pdf" | "excel",
  "start_date": "2025-05-01",
  "end_date": "2025-05-31",
  "brand_id": 1,
  "include_sections": ["insights", "overview", "products", "delivery"]
}
```

**Response:**
```json
{
  "download_url": "/downloads/report_maria_2025-05.pdf",
  "expires_at": "2025-10-30T23:59:59Z"
}
```

**Dependências:**
- Backend: `reportlab` (PDF) ou `openpyxl` (Excel)
- Gerar arquivo temporário
- Servir via endpoint `/downloads/{filename}`

**Template do Relatório:**
```
┌──────────────────────────────────────────────────┐
│ RELATÓRIO EXECUTIVO - MAIO/2025                  │
│ Maria - Burguer Boutique                         │
├──────────────────────────────────────────────────┤
│                                                  │
│ 📊 RESUMO DO PERÍODO                             │
│ Receita: R$ 234.500 (+12% vs Abril)             │
│ Pedidos: 3.240 (-3% vs Abril)                   │
│ Ticket Médio: R$ 72,40 (+15% vs Abril)          │
│                                                  │
│ ⚠️ INSIGHTS CRÍTICOS                             │
│ 1. Perda de R$ 12.400 em cancelamentos delivery │
│    → Recomendação: Adicionar 2 entregadores     │
│                                                  │
│ 2. 23 clientes VIP inativos (R$ 34k em risco)   │
│    → Recomendação: Campanha reativação          │
│                                                  │
│ 🎯 OPORTUNIDADES                                 │
│ 1. Item "X-Bacon Premium" com alta margem       │
│    → Recomendação: Destacar no delivery         │
│                                                  │
│ [GRÁFICOS E TABELAS...]                          │
│                                                  │
└──────────────────────────────────────────────────┘
```

---

### ✅ Checklist de Conclusão - Sprint 2

**Backend:**
- [ ] Detectores de padrões temporais implementados
- [ ] Detectores de correlações implementados
- [ ] Previsão de demanda (7 dias) implementada
- [ ] Previsão de churn iminente implementada
- [ ] Endpoint `/export/report` implementado
- [ ] Geração de PDF/Excel funcional

**Frontend:**
- [ ] Insights de padrões exibidos no `InsightsPanel`
- [ ] Insights preditivos exibidos
- [ ] `ExportButton` melhorado com opções PDF/Excel
- [ ] Download de relatório funcional

**Validação:**
- [ ] Sistema detecta padrões temporais (ex: "Segundas vendem 30% menos")
- [ ] Sistema sugere ações baseadas em previsões
- [ ] Relatório PDF/Excel é gerado e baixado corretamente
- [ ] Relatório inclui insights + narrativa + gráficos

---

## 🎨 SPRINT 3: Templates por Persona + Favoritos (3-4 dias)

### 🎯 Objetivo
Cada usuário vê o que importa para seu papel, sem complexidade de "query builder".

### 📦 Entregas

#### **3.1 Sistema de Templates de Dashboard** (2 dias)

##### **Backend: Gerenciamento de Templates**
**Arquivo:** `backend/app/api/routes/dashboards.py` (novo)

**Endpoints:**
```python
GET /api/v1/dashboards/templates
GET /api/v1/dashboards/templates/{template_id}
POST /api/v1/dashboards/user-config  # Salvar preferências
GET /api/v1/dashboards/user-config   # Buscar preferências
```

**Templates pré-definidos:**

1. **Template "Proprietário"**
```json
{
  "id": "owner",
  "name": "Visão do Proprietário",
  "description": "Foco em lucro, comparação de lojas e insights estratégicos",
  "sections": [
    {"type": "insights", "priority": 1},
    {"type": "overview_kpis", "priority": 2},
    {"type": "store_comparison", "priority": 3},
    {"type": "products_top", "limit": 5, "priority": 4},
    {"type": "channels_performance", "priority": 5}
  ]
}
```

2. **Template "Gerente Operacional"**
```json
{
  "id": "manager",
  "name": "Visão do Gerente",
  "description": "Foco em operação, delivery e produtos",
  "sections": [
    {"type": "insights", "filters": ["performance_issue", "opportunity"], "priority": 1},
    {"type": "delivery_performance", "priority": 2},
    {"type": "products_by_context", "priority": 3},
    {"type": "hourly_distribution", "priority": 4},
    {"type": "overview_kpis", "priority": 5}
  ]
}
```

3. **Template "Marketing/CRM"**
```json
{
  "id": "marketing",
  "name": "Visão de Marketing",
  "description": "Foco em clientes, canais e churn",
  "sections": [
    {"type": "insights", "filters": ["churn_risk", "customer_behavior"], "priority": 1},
    {"type": "churn_risk_table", "priority": 2},
    {"type": "rfm_analysis", "priority": 3},
    {"type": "channels_performance", "priority": 4},
    {"type": "products_top", "priority": 5}
  ]
}
```

##### **Frontend: Seletor de Template**
**Arquivo:** `frontend/src/components/dashboard/DashboardTemplateSelector.tsx`

**UI:**
```
┌─────────────────────────────────────────────────┐
│ 👤 Selecione sua Visão                           │
├─────────────────────────────────────────────────┤
│                                                 │
│  📊 Proprietário                                │
│  Foco em lucro e comparação de lojas           │
│  [Selecionar]                                   │
│                                                 │
│  ⚙️ Gerente Operacional                         │
│  Foco em operação e delivery                    │
│  [Selecionar]                                   │
│                                                 │
│  📢 Marketing/CRM                               │
│  Foco em clientes e canais                      │
│  [Selecionar]                                   │
│                                                 │
└─────────────────────────────────────────────────┘
```

##### **Componente Dinâmico de Dashboard**
**Arquivo:** `frontend/src/components/dashboard/DynamicDashboard.tsx`

**Funcionalidade:**
- [ ] Buscar template selecionado (ou padrão)
- [ ] Renderizar seções dinamicamente baseado em `sections`
- [ ] Respeitar ordem (`priority`)
- [ ] Cada `type` mapeia para um componente:
  - `insights` → `<InsightsPanel />`
  - `overview_kpis` → `<KPICards />`
  - `store_comparison` → `<StoreComparisonView />`
  - `products_top` → `<TopProductsTable />`
  - etc.

---

#### **3.2 Sistema de Favoritos** (1 dia)

##### **Funcionalidade:**
- [ ] Usuário pode "favoritar" cards/métricas específicas
- [ ] Cards favoritados aparecem primeiro (antes do template)
- [ ] Favoritos salvos no backend ou localStorage

**UI:**
- [ ] Ícone de estrela em cada card
- [ ] Seção "Meus Favoritos" no topo do dashboard

**Backend:**
```python
POST /api/v1/dashboards/favorites
{
  "section_type": "products_by_context",
  "filters": {"weekday": 5, "channel_id": 3}
}

GET /api/v1/dashboards/favorites
DELETE /api/v1/dashboards/favorites/{id}
```

---

#### **3.3 Customização Leve (Opcional)** (1 dia se houver tempo)

##### **Funcionalidade:**
- [ ] Dentro de um template, usuário pode:
  - Reordenar seções (drag & drop)
  - Ocultar seções específicas
  - Ajustar parâmetros (ex: top 5 ou top 10 produtos)

**Não implementar:**
- ❌ Query builder complexo
- ❌ Criação de métricas do zero
- ❌ SQL visual

---

### ✅ Checklist de Conclusão - Sprint 3

**Backend:**
- [ ] Endpoints de templates implementados
- [ ] 3 templates pré-definidos (Owner, Manager, Marketing)
- [ ] Endpoints de favoritos implementados
- [ ] Salvamento de preferências de usuário

**Frontend:**
- [ ] `DashboardTemplateSelector` criado
- [ ] `DynamicDashboard` criado (renderização dinâmica)
- [ ] Sistema de favoritos implementado
- [ ] Persistência de template selecionado (localStorage ou backend)

**Validação:**
- [ ] Usuário seleciona "Visão do Proprietário" e vê seções corretas
- [ ] Usuário seleciona "Visão do Gerente" e dashboard reorganiza
- [ ] Favoritar um card move ele para o topo
- [ ] Preferências persistem após reload da página

---

## 📈 Métricas de Sucesso

### Validação com Persona (Maria)

Testar se Maria consegue, em **< 5 minutos**:

| Tarefa | Como Validar | Tempo Esperado |
|--------|--------------|----------------|
| Ver overview do mês | Abrir dashboard → Insights + KPIs visíveis | < 30s |
| Identificar top 10 produtos no delivery | Filtrar canal "iFood" → Ver tabela | < 1min |
| Comparar 2 lojas | Clicar "Comparar Lojas" → Selecionar 2 → Ver métricas | < 2min |
| Exportar relatório para sócio | Clicar "Exportar" → Baixar PDF | < 1min |
| **TOTAL** | | **< 5min ✅** |

### Validação Técnica

- [ ] Insights carregam em < 2s (mesmo com milhões de registros)
- [ ] Queries otimizadas (usar EXPLAIN ANALYZE)
- [ ] Frontend responsivo (mobile funcional)
- [ ] Sem bugs visuais (testar em Chrome/Firefox/Safari)

---

## 🚧 Riscos e Mitigações

| Risco | Impacto | Mitigação |
|-------|---------|-----------|
| Queries lentas com milhões de registros | Alto | Criar índices, limitar período padrão a 30 dias |
| Insights irrelevantes/falsos positivos | Médio | Ajustar thresholds, adicionar mínimo de volume |
| Complexidade do frontend | Médio | Começar simples (MVP), iterar depois |
| Falta de dados para testar insights | Baixo | `generate_data.py` já tem 6 meses + contextos variados |

---

## 📚 Arquivos Criados/Modificados

### Novos Arquivos Backend
- [ ] `backend/app/api/routes/insights.py`
- [ ] `backend/app/services/insights_engine.py`
- [ ] `backend/app/api/routes/dashboards.py`

### Novos Arquivos Frontend
- [ ] `frontend/src/components/insights/InsightsPanel.tsx`
- [ ] `frontend/src/components/insights/InsightCard.tsx`
- [ ] `frontend/src/components/insights/InsightIcon.tsx`
- [ ] `frontend/src/components/dashboard/StoreComparisonView.tsx`
- [ ] `frontend/src/components/dashboard/DashboardTemplateSelector.tsx`
- [ ] `frontend/src/components/dashboard/DynamicDashboard.tsx`
- [ ] `frontend/src/types/insights.ts`

### Arquivos Modificados
- [ ] `backend/app/models/schemas.py` (adicionar schemas de insights)
- [ ] `frontend/src/components/dashboard/Dashboard.tsx` (integrar insights)
- [ ] `frontend/src/components/filters/ChannelFilter.tsx` (melhorar)
- [ ] `frontend/src/components/ExportButton.tsx` (melhorar)

---

## 🎯 Próximos Passos Imediatos

### Para Começar Sprint 1:
1. ✅ Criar este arquivo `ROADMAP_INSIGHTS.md`
2. 🔄 Mudar para Agent Mode no Cursor
3. ▶️ Começar por: "Implemente o componente InsightsPanel.tsx conforme Sprint 1"

### Comandos Úteis
```bash
# Verificar se backend está rodando
curl http://localhost:8000/docs

# Verificar se frontend está rodando
# Acessar http://localhost:5173

# Ver logs do backend
docker compose logs -f backend

# Recarregar dados (se necessário)
# Ver arquivo docs/REGERAR_DADOS.md para instruções completas
docker compose down postgres -v
docker compose up -d postgres
# Aguardar inicialização...
docker compose run --rm data-generator
```

---

## 💬 Notas Finais

**Filosofia do Projeto:**
> "Não mostre dados. Mostre decisões."

**Diferencial:**
- Outros: "Aqui está um gráfico, interprete"
- Nós: "⚠️ Você está perdendo R$ 12k. Faça isso →"

**Lembretes:**
- Sempre priorizar **insights acionáveis** sobre métricas genéricas
- Manter UX simples (< 5min para decisão)
- Testar com dados reais do `generate_data.py`

---

**Última atualização:** 30/10/2025  
**Status:** 📋 Roadmap completo - Pronto para Sprint 1

