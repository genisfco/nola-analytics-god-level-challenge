# 🏢 Sistema de Brands no Frontend

Documentação do sistema de seleção de brands (proprietários) implementado no frontend.

## 📁 Arquivos Criados

```
frontend/src/
├── contexts/
│   └── BrandContext.tsx         # Context API para gerenciar brand
├── components/
│   ├── BrandSelector.tsx        # Componente de seleção de brand
│   └── filters/
│       └── StoreFilter.tsx      # Atualizado para buscar stores da API
├── App.tsx                      # Atualizado com BrandSelector
└── main.tsx                     # Atualizado com BrandProvider
```

## 🎯 Componentes

### 1. BrandContext

Context API que gerencia o estado global do brand selecionado.

**Funcionalidades:**
- Busca lista de brands da API
- Persiste brand selecionado no localStorage
- Seleciona automaticamente o primeiro brand se nenhum estiver selecionado
- Compartilha estado entre todos os componentes

**Hook:**
```typescript
import { useBrand } from '../contexts/BrandContext'

const { brandId, brandName, brands, setBrand, loading } = useBrand()
```

**Propriedades:**
- `brandId: number | null` - ID do brand selecionado
- `brandName: string | null` - Nome do brand selecionado
- `brands: Brand[]` - Lista de todos os brands disponíveis
- `setBrand: (id, name) => void` - Função para trocar de brand
- `loading: boolean` - Estado de carregamento

---

### 2. BrandSelector

Componente dropdown para seleção do proprietário (brand).

**Características:**
- Exibe ícone de prédio (Building2)
- Lista todos os brands disponíveis
- Salva seleção no localStorage
- Recarrega página ao trocar de brand (para atualizar todos os dados)
- Estado de loading com animação

**Uso:**
```tsx
import { BrandSelector } from './components/BrandSelector'

<BrandSelector />
```

**Visual:**
```
┌─────────────────────────────────────────┐
│ 🏢 Proprietário: [Maria - Burguer... ▼] │
└─────────────────────────────────────────┘
```

---

### 3. StoreFilter (Atualizado)

Filtro de lojas que busca dinamicamente da API baseado no brand selecionado.

**Mudanças:**
- ✅ Remove dados mockados
- ✅ Busca stores via API `/api/v1/analytics/stores/list?brand_id=X`
- ✅ Atualiza automaticamente quando brand muda
- ✅ Mostra cidade e estado de cada loja
- ✅ Exibe contador de lojas disponíveis
- ✅ Loading state

**Uso:**
```tsx
import { StoreFilter } from './components/filters/StoreFilter'

<StoreFilter
  onApply={(storeIds) => console.log('Selected stores:', storeIds)}
  initialStores={[]}
/>
```

---

## 🔄 Fluxo de Dados

```
1. App Inicializa
   └─> BrandProvider busca /brands/list
       └─> Seleciona primeiro brand automaticamente
           └─> Salva no localStorage

2. Usuário Abre Dashboard
   └─> StoreFilter lê brandId do context
       └─> Busca /stores/list?brand_id=X
           └─> Exibe lojas filtradas

3. Usuário Troca Brand
   └─> BrandSelector.onChange()
       └─> setBrand(newId, newName)
           └─> Salva no localStorage
               └─> window.location.reload()
                   └─> Recarrega com novo brand
```

---

## 📡 Endpoints Utilizados

### GET `/api/v1/analytics/brands/list`
Retorna lista de todos os brands disponíveis.

```json
{
  "brands": [
    { "id": 1, "name": "Maria - Burguer Boutique" },
    { "id": 2, "name": "João - Pizza & Cia" }
  ],
  "total": 7
}
```

### GET `/api/v1/analytics/stores/list?brand_id={id}`
Retorna lojas do brand específico.

```json
{
  "stores": [
    {
      "id": 1,
      "name": "Cavalcante - da Mota",
      "city": "da Mota",
      "state": "AP",
      "is_active": true
    }
  ],
  "total": 3,
  "brand_id": 1
}
```

---

## 💾 LocalStorage

O sistema persiste os seguintes dados:

```
selectedBrandId: "1"
selectedBrandName: "Maria - Burguer Boutique"
```

Isso permite que o usuário mantenha sua seleção entre sessões.

---

## 🎨 Estilo Visual

### BrandSelector
- Background: `bg-card`
- Border: `border-b border-border`
- Shadow: `shadow-sm`
- Padding: `p-4`

### StoreFilter
- Cards com hover effect
- Checkboxes estilizados
- Scroll vertical quando necessário (`max-h-64`)
- Badges para lojas selecionadas

---

## 🚀 Como Usar em Novos Componentes

### Acessar Brand Atual
```tsx
import { useBrand } from '../contexts/BrandContext'

function MyComponent() {
  const { brandId, brandName } = useBrand()
  
  // Usar brandId nas queries
  const fetchData = async () => {
    const response = await fetch(
      `http://localhost:8000/api/v1/analytics/data?brand_id=${brandId}`
    )
    return response.json()
  }
}
```

### Recarregar Dados ao Trocar Brand
```tsx
useEffect(() => {
  if (brandId) {
    fetchData()
  }
}, [brandId]) // Reexecuta quando brand muda
```

---

## ✅ Checklist de Implementação

- [x] BrandContext criado
- [x] BrandProvider adicionado ao main.tsx
- [x] BrandSelector implementado
- [x] StoreFilter atualizado para usar API
- [x] Persistência em localStorage
- [x] Loading states
- [x] Seleção automática do primeiro brand
- [ ] Adicionar brand_id em todas as queries de analytics
- [ ] Criar hook customizado `useApi()` para facilitar
- [ ] Atualizar Dashboard para usar brandId
- [ ] Atualizar AdvancedDashboard para usar brandId

---

## 🔧 Próximos Passos

1. **Criar hook `useApi`** para centralizar chamadas com brand_id:
```tsx
const { fetchWithBrand } = useApi()
const data = await fetchWithBrand('/overview', { start_date, end_date })
```

2. **Atualizar todos os componentes de dashboard** para incluir brand_id nas queries

3. **Adicionar filtro de brand opcional** para admin visualizar todos os brands

4. **Otimizar reload** - Em vez de `window.location.reload()`, usar invalidação de cache do React Query

---

## 📝 Notas

- Sistema de brands é **obrigatório** - sempre há um brand selecionado
- Cada brand vê apenas suas próprias lojas e dados
- Maria tem 3 lojas (menor proprietário)
- Outros brands têm 7-8 lojas cada
- Total: 50 lojas distribuídas entre 7 brands

