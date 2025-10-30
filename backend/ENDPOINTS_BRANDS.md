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

1. **Brand Selector**: Popular dropdown com lista de proprietários
2. **Store Filter**: Popular filtro de lojas baseado no brand selecionado
3. **Context Isolation**: Garantir que cada proprietário veja apenas seus dados

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

## 🚀 Próximos Passos

1. ✅ Backend: Endpoints criados
2. ⏳ Frontend: Criar BrandContext
3. ⏳ Frontend: Criar BrandSelector component
4. ⏳ Frontend: Atualizar StoreFilter para usar API
5. ⏳ Backend: Adicionar `brand_id` em todos os endpoints existentes
6. ⏳ Frontend: Atualizar todas as queries para incluir `brand_id`

## 📝 Notas

- Apenas lojas ativas (`is_active=true`) são retornadas
- A ordenação é alfabética por nome
- Encoding UTF-8 está configurado para nomes em português

