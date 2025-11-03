# 🏢 Endpoints de Brands e Stores

Documentação dos novos endpoints implementados para suportar múltiplos proprietários (brands).

## 📋 Endpoints Disponíveis

### 1. GET `/api/v1/analytics/brands/list`

Lista todos os brands (proprietários) disponíveis.

**Parâmetros:** Nenhum

**Resposta:**
```json
{
  "brands": [
    {
      "id": 1,
      "name": "Maria - Burguer Boutique"
    },
    {
      "id": 2,
      "name": "João - Pizza & Cia"
    }
  ],
  "total": 7
}
```

**Exemplo de uso:**
```bash
curl http://localhost:8000/api/v1/analytics/brands/list
```

---

### 2. GET `/api/v1/analytics/stores/list`

Lista todas as lojas de um brand específico.

**Parâmetros:**
- `brand_id` (required): ID do brand para filtrar lojas

**Resposta:**
```json
{
  "stores": [
    {
      "id": 1,
      "name": "Cavalcante - da Mota",
      "city": "da Mota",
      "state": "AP",
      "is_active": true
    },
    {
      "id": 2,
      "name": "Leão - Pastor das Pedras",
      "city": "Pastor das Pedras",
      "state": "PE",
      "is_active": true
    }
  ],
  "total": 3,
  "brand_id": 1
}
```

**Exemplo de uso:**
```bash
# Listar lojas de Maria (brand_id=1)
curl "http://localhost:8000/api/v1/analytics/stores/list?brand_id=1"

# PowerShell
Invoke-WebRequest -Uri "http://localhost:8000/api/v1/analytics/stores/list?brand_id=1"
```

---

## 🎯 Caso de Uso

Estes endpoints são usados para:

1. **Brand Selector**: Popular dropdown com lista de proprietários ✅ Implementado
2. **Store Filter**: Popular filtro de lojas baseado no brand selecionado ✅ Implementado
3. **Context Isolation**: Garantir que cada proprietário veja apenas seus dados ✅ Implementado

**Integração Frontend:**
- `BrandContext` usa `/brands/list` para carregar lista de brands
- `StoreFilter` usa `/stores/list?brand_id=X` para carregar lojas do brand selecionado
- `useApi()` hook adiciona `brand_id` automaticamente em todas as outras requisições

## 📊 Distribuição Atual dos Dados

```
Maria - Burguer Boutique       → 3 lojas
João - Pizza & Cia             → 8 lojas
Ana - Sushi House              → 7 lojas
Carlos - Food Center           → 8 lojas
Pedro - Restaurante Popular    → 8 lojas
Lucia - Bistrô Moderno         → 8 lojas
Roberto - Fast Food Network    → 8 lojas
──────────────────────────────────────────
Total                          → 50 lojas
```

## 🔧 Schemas Pydantic

```python
# Brand
class Brand(BaseModel):
    id: int
    name: str

# Store
class Store(BaseModel):
    id: int
    name: str
    city: Optional[str]
    state: Optional[str]
    is_active: bool

# Response wrappers
class BrandsListResponse(BaseModel):
    brands: list[Brand]
    total: int

class StoresListResponse(BaseModel):
    stores: list[Store]
    total: int
    brand_id: int
```

## ✅ Testes Realizados

```bash
# ✅ Listar todos os brands
curl http://localhost:8000/api/v1/analytics/brands/list
# Retorna: 7 brands

# ✅ Listar lojas de Maria (brand_id=1)
curl "http://localhost:8000/api/v1/analytics/stores/list?brand_id=1"
# Retorna: 3 lojas

# ✅ Listar lojas de João (brand_id=2)
curl "http://localhost:8000/api/v1/analytics/stores/list?brand_id=2"
# Retorna: 8 lojas
```

## ✅ Status de Implementação

### Backend ✅ COMPLETO
1. ✅ Endpoints `/brands/list` e `/stores/list` criados e funcionando
2. ✅ Parâmetro `brand_id` adicionado em **todos** os endpoints de analytics:
   - `/overview` - Filtra por brand
   - `/products/top` - Filtra por brand
   - `/channels` - Filtra por brand
   - `/stores` - Filtra por brand
   - `/sales/trend` - Filtra por brand
   - `/sales/hourly` - Filtra por brand
   - `/sales/weekday` - Filtra por brand
   - `/categories` - Filtra por brand
   - `/insights/automatic` - **Requer brand_id** (obrigatório)
   - Endpoints avançados também suportam `brand_id`

### Frontend ✅ COMPLETO
1. ✅ `BrandContext` criado e funcionando
2. ✅ `BrandSelector` component criado e integrado
3. ✅ `StoreFilter` atualizado para buscar lojas via API
4. ✅ Hook `useApi()` criado - adiciona `brand_id` automaticamente em todas as requisições
5. ✅ Todos os dashboards (`Dashboard`, `AdvancedDashboard`) usando `brandId`
6. ✅ Todas as queries incluem `brandId` no queryKey

**Nota:** O hook `useApi()` adiciona `brand_id` automaticamente, então não é necessário passar manualmente em cada requisição.

## 📝 Notas Técnicas

- **Filtro de lojas**: Apenas lojas ativas (`is_active=true`) são retornadas
- **Ordenação**: Lojas ordenadas alfabeticamente por nome
- **Encoding**: UTF-8 configurado para nomes em português
- **Parâmetro brand_id**: 
  - Obrigatório em `/stores/list`
  - Opcional (mas recomendado) nos outros endpoints
  - Obrigatório em `/insights/automatic`
- **Integração automática**: O hook `useApi()` do frontend adiciona `brand_id` automaticamente

## 🔗 Relacionados

- Documentação completa: [IMPLEMENTACAO_BRANDS.md](./IMPLEMENTACAO_BRANDS.md)

