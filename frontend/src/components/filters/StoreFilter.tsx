import { Store as StoreIcon } from 'lucide-react'
import { useState, useEffect } from 'react'
import { useBrand } from '../../contexts/BrandContext'

interface Store {
  id: number
  name: string
  city: string | null
  state: string | null
  is_active: boolean
}

interface StoreFilterProps {
  onApply: (storeIds: number[]) => void
  initialStores?: number[]
  layout?: 'vertical' | 'horizontal'
}

export function StoreFilter({ onApply, initialStores = [], layout = 'vertical' }: StoreFilterProps) {
  const { brandId } = useBrand()
  const [selectedStores, setSelectedStores] = useState<number[]>(initialStores)
  const [storeOptions, setStoreOptions] = useState<Store[]>([])
  const [loading, setLoading] = useState(true)

  // Sincronizar quando initialStores mudarem (ex: vindo de insight)
  useEffect(() => {
    if (initialStores) {
      // Só atualiza se for diferente do estado atual
      const currentIds = selectedStores.sort().join(',')
      const newIds = initialStores.sort().join(',')
      if (currentIds !== newIds) {
        setSelectedStores(initialStores)
        // Aplicar automaticamente quando vier de insight
        onApply(initialStores)
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [initialStores])

  // Fetch stores when brand changes
  useEffect(() => {
    const fetchStores = async () => {
      if (!brandId) return
      
      setLoading(true)
      try {
        const response = await fetch(
          `/api/v1/analytics/stores/list?brand_id=${brandId}`
        )
        const data = await response.json()
        setStoreOptions(data.stores)
      } catch (error) {
        console.error('Error fetching stores:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchStores()
  }, [brandId])

  const handleStoreToggle = (storeId: number) => {
    setSelectedStores((prev) => {
      const newStores = prev.includes(storeId)
        ? prev.filter((id) => id !== storeId)
        : [...prev, storeId]
      // Aplicar automaticamente quando uma loja é selecionada/deselecionada
      onApply(newStores)
      return newStores
    })
  }

  const handleSelectAll = () => {
    const newStores = selectedStores.length === storeOptions.length
      ? []
      : storeOptions.map((store) => store.id)
    setSelectedStores(newStores)
    // Aplicar automaticamente quando seleciona/deseleciona todas
    onApply(newStores)
  }

  const handleClear = () => {
    setSelectedStores([])
    onApply([])
  }

  const hasFilters = selectedStores.length > 0

  const allSelected = selectedStores.length === storeOptions.length

  if (loading) {
    return (
      <div className="bg-card rounded-lg shadow-sm border border-border p-4">
        <div className="flex items-center gap-2 mb-4">
          <StoreIcon className="w-4 h-4 text-primary animate-pulse" />
          <h3 className="font-semibold text-card-foreground">Lojas</h3>
        </div>
        <div className="flex items-center justify-center py-8">
          <div className="text-sm text-muted-foreground">Carregando lojas...</div>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-card rounded-lg shadow-sm border border-border p-4">
      <div className="flex items-center gap-2 mb-4">
        <StoreIcon className="w-4 h-4 text-primary" />
        <h3 className="font-semibold text-card-foreground">Lojas</h3>
        <span className="text-xs text-muted-foreground ml-auto">
          ({storeOptions.length} disponíveis)
        </span>
      </div>

      <div className="space-y-4">
        {/* Select All/None Toggle */}
        <button
          onClick={handleSelectAll}
          className="w-full px-3 py-2 text-sm bg-primary/10 hover:bg-primary/20 text-primary rounded-md transition-colors font-medium"
        >
          {allSelected ? 'Desmarcar Todas' : 'Selecionar Todas'}
        </button>

        {/* Store Checkboxes */}
        <div className={layout === 'horizontal' 
          ? "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2 max-h-64 overflow-y-auto" 
          : "space-y-2 max-h-64 overflow-y-auto"}>
          {storeOptions.map((store) => (
            <label
              key={store.id}
              className="flex items-center gap-2 p-2 rounded-md hover:bg-accent/50 cursor-pointer transition-colors"
            >
              <input
                type="checkbox"
                checked={selectedStores.includes(store.id)}
                onChange={() => handleStoreToggle(store.id)}
                className="w-4 h-4 text-primary border-border rounded focus:ring-2 focus:ring-primary accent-primary flex-shrink-0"
              />
              <div className="flex flex-col flex-1 min-w-0">
                <span className="text-sm text-card-foreground font-medium truncate">{store.name}</span>
                {(store.city || store.state) && (
                  <span className="text-xs text-muted-foreground truncate">
                    {store.city}{store.city && store.state && ', '}{store.state}
                  </span>
                )}
              </div>
            </label>
          ))}
        </div>

        {/* Clear Button */}
        {hasFilters && (
          <div className="flex gap-2">
            <button
              onClick={handleClear}
              className="w-full px-4 py-2 bg-muted hover:bg-muted/80 text-muted-foreground rounded-md font-medium transition-colors"
            >
              Limpar Filtros
            </button>
          </div>
        )}

        {/* Active Filters Display */}
        {hasFilters && (
          <div className="pt-3 border-t border-border">
            <p className="text-xs font-medium text-muted-foreground mb-2">
              {selectedStores.length === storeOptions.length
                ? 'Todas as lojas selecionadas'
                : `${selectedStores.length} loja${selectedStores.length > 1 ? 's' : ''} selecionada${selectedStores.length > 1 ? 's' : ''}:`}
            </p>
            {selectedStores.length < storeOptions.length && (
              <div className="flex flex-wrap gap-2">
                {selectedStores.map((storeId) => {
                  const store = storeOptions.find((s) => s.id === storeId)
                  return (
                    <span
                      key={storeId}
                      className="inline-flex items-center px-2 py-1 bg-primary/10 text-primary text-xs rounded-md"
                    >
                      {store?.name}
                    </span>
                  )
                })}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

