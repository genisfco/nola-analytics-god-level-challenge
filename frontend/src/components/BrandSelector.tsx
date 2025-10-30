import { Building2 } from 'lucide-react'
import { useBrand } from '../contexts/BrandContext'

export function BrandSelector() {
  const { brandId, brandName, brands, setBrand, loading } = useBrand()

  if (loading) {
    return (
      <div className="flex items-center gap-3 p-4 bg-card border-b border-border">
        <Building2 className="w-5 h-5 text-primary animate-pulse" />
        <span className="text-sm text-muted-foreground">Carregando proprietários...</span>
      </div>
    )
  }

  return (
    <div className="flex items-center gap-3 p-4 bg-card border-b border-border shadow-sm">
      <Building2 className="w-5 h-5 text-primary" />
      <span className="text-sm font-medium text-muted-foreground">
        Proprietário:
      </span>
      <select
        value={brandId || ''}
        onChange={(e) => {
          const id = parseInt(e.target.value)
          const brand = brands.find(b => b.id === id)
          if (brand) {
            setBrand(brand.id, brand.name)
            // Reload page to refresh all data
            window.location.reload()
          }
        }}
        className="px-3 py-1.5 border border-border rounded-md text-sm font-semibold bg-background focus:outline-none focus:ring-2 focus:ring-primary transition-all"
      >
        {brands.map(brand => (
          <option key={brand.id} value={brand.id}>
            {brand.name}
          </option>
        ))}
      </select>
      {brandName && (
        <span className="text-xs text-muted-foreground px-2 py-1 bg-primary/5 rounded-md">
          {brands.find(b => b.id === brandId)?.name.split(' - ')[1] || ''}
        </span>
      )}
    </div>
  )
}

