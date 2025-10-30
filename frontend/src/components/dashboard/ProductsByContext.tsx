import { useQuery } from '@tanstack/react-query'
import { Package, TrendingUp } from 'lucide-react'
import { useApi } from '@/hooks/useApi'
import { useBrand } from '@/contexts/BrandContext'
import { ProductByContext } from '@/lib/api'
import { formatCurrency, formatNumber } from '@/lib/utils'
import { ContextFilters } from '../filters/AdvancedFilters'

interface ProductsByContextResponse {
  products: ProductByContext[]
  total_products: number
  context: Record<string, any>
  period: {
    start_date: string
    end_date: string
  }
}

interface ProductsByContextProps {
  startDate: string
  endDate: string
  contextFilters: ContextFilters
}

export function ProductsByContext({ startDate, endDate, contextFilters }: ProductsByContextProps) {
  const { fetchApi } = useApi()
  const { brandId } = useBrand()

  const hasContextFilters = 
    contextFilters.weekday !== undefined || 
    contextFilters.hourStart !== undefined || 
    contextFilters.channelId !== undefined

  const { data, isLoading } = useQuery<ProductsByContextResponse>({
    queryKey: ['products-context', startDate, endDate, contextFilters, brandId],
    queryFn: () =>
      fetchApi<ProductsByContextResponse>('/products/by-context', {
        start_date: startDate,
        end_date: endDate,
        weekday: contextFilters.weekday,
        hour_start: contextFilters.hourStart,
        hour_end: contextFilters.hourEnd,
        channel_id: contextFilters.channelId,
        limit: 10,
      }),
    enabled: hasContextFilters && !!brandId,
  })

  if (!hasContextFilters) {
    return (
      <div className="bg-card rounded-lg shadow-sm border border-border p-6">
        <div className="flex items-center gap-2 mb-4">
          <Package className="w-5 h-5 text-primary" />
          <h3 className="text-lg font-semibold text-card-foreground">
            Produtos mais vendidos
          </h3>
        </div>
        <div className="text-center py-8">
          <Package className="w-12 h-12 text-muted-foreground mx-auto mb-2" />
          <p className="text-muted-foreground mb-2">
            Selecione filtros contextuais para ver os produtos mais vendidos
          </p>          
        </div>
      </div>
    )
  }

  if (isLoading) {
    return (
      <div className="bg-card rounded-lg shadow-sm border border-border p-6">
        <p className="text-muted-foreground text-center">Carregando produtos...</p>
      </div>
    )
  }

  if (!data || !data.products || data.products.length === 0) {
    return (
      <div className="bg-card rounded-lg shadow-sm border border-border p-6">
        <div className="flex items-center gap-2 mb-4">
          <Package className="w-5 h-5 text-primary" />
          <h3 className="text-lg font-semibold text-card-foreground">
            Produtos mais vendidos
          </h3>
        </div>
        <div className="text-center py-8">
          <p className="text-muted-foreground">
            Nenhum produto encontrado com os filtros selecionados
          </p>
        </div>
      </div>
    )
  }

  const products: ProductByContext[] = data.products
  const weekdayNames = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
  
  const contextLabel = []
  if (contextFilters.weekday !== undefined) {
    contextLabel.push(weekdayNames[contextFilters.weekday])
  }
  if (contextFilters.hourStart !== undefined && contextFilters.hourEnd !== undefined) {
    contextLabel.push(`${contextFilters.hourStart}h-${contextFilters.hourEnd}h`)
  }

  return (
    <div className="bg-card rounded-lg shadow-sm border border-border p-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Package className="w-5 h-5 text-primary" />
          <h3 className="text-lg font-semibold text-card-foreground">
            Top Produtos {contextLabel.length > 0 && `- ${contextLabel.join(' • ')}`}
          </h3>
        </div>
        <span className="text-sm text-muted-foreground">
          {products.length} produtos
        </span>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-border">
              <th className="text-left py-3 px-4 text-sm font-semibold text-muted-foreground">
                #
              </th>
              <th className="text-left py-3 px-4 text-sm font-semibold text-muted-foreground">
                Produto
              </th>
              <th className="text-left py-3 px-4 text-sm font-semibold text-muted-foreground">
                Categoria
              </th>
              <th className="text-right py-3 px-4 text-sm font-semibold text-muted-foreground">
                Vendas
              </th>
              <th className="text-right py-3 px-4 text-sm font-semibold text-muted-foreground">
                Faturamento
              </th>
              <th className="text-right py-3 px-4 text-sm font-semibold text-muted-foreground">
                Preço Médio
              </th>
            </tr>
          </thead>
          <tbody>
            {products.map((product, index) => (
              <tr
                key={product.product_id}
                className="border-b border-border last:border-0 hover:bg-primary/5 transition-colors"
              >
                <td className="py-3 px-4 text-sm font-bold text-primary">
                  {index + 1}
                </td>
                <td className="py-3 px-4">
                  <p className="text-sm font-medium text-card-foreground">
                    {product.product_name}
                  </p>
                </td>
                <td className="py-3 px-4 text-sm text-muted-foreground">
                  {product.category || '-'}
                </td>
                <td className="py-3 px-4 text-sm text-right">
                  <span className="inline-flex items-center gap-1">
                    <TrendingUp className="w-3 h-3 text-green-600" />
                    {formatNumber(product.times_sold)}
                  </span>
                </td>
                <td className="py-3 px-4 text-sm text-right font-semibold text-primary">
                  {formatCurrency(product.total_revenue)}
                </td>
                <td className="py-3 px-4 text-sm text-right text-muted-foreground">
                  {formatCurrency(product.avg_price)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="mt-4 p-3 bg-primary/5 border border-primary/20 rounded-lg">
        <p className="text-sm text-card-foreground">
          <strong className="text-primary">💡 Insight:</strong>{' '}
          O produto <strong>{products[0].product_name}</strong> é o campeão
          {contextLabel.length > 0 && ` ${contextLabel.join(' ')}`}, faturando{' '}
          <strong>{formatCurrency(products[0].total_revenue)}</strong> com{' '}
          <strong>{formatNumber(products[0].times_sold)} vendas</strong>.
        </p>
      </div>
    </div>
  )
}

