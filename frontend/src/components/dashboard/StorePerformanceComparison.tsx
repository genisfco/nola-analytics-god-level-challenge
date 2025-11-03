import { useQuery } from '@tanstack/react-query'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts'
import { Store, TrendingUp, MapPin } from 'lucide-react'
import { useApi } from '@/hooks/useApi'
import { useBrand } from '@/contexts/BrandContext'
import { StoreMetrics } from '@/lib/api'
import { formatCurrency, formatNumber, formatPercent } from '@/lib/utils'
import { ContextFilters } from '../filters/AdvancedFilters'

interface StorePerformanceResponse {
  stores: StoreMetrics[]
  total_stores: number
  period: {
    start_date: string
    end_date: string
  }
}

interface StorePerformanceComparisonProps {
  startDate: string
  endDate: string
  contextFilters?: ContextFilters
  storeIds?: number[]
}

const COLORS = ['#fd6263', '#8b1721', '#3b82f6', '#f59e0b', '#10b981', '#6366f1', '#ec4899', '#14b8a6']

export function StorePerformanceComparison({ 
  startDate, 
  endDate, 
  contextFilters, 
  storeIds 
}: StorePerformanceComparisonProps) {
  const { fetchApi } = useApi()
  const { brandId } = useBrand()

  const { data, isLoading } = useQuery<StorePerformanceResponse>({
    queryKey: ['store-performance', startDate, endDate, contextFilters, storeIds, brandId],
    queryFn: () => fetchApi<StorePerformanceResponse>('/stores/performance', {
      start_date: startDate,
      end_date: endDate,
      brand_id: brandId,
      weekday: contextFilters?.weekday,
      hour_start: contextFilters?.hourStart,
      hour_end: contextFilters?.hourEnd,
      channel_id: contextFilters?.channelId,
      store_ids: storeIds && storeIds.length > 0 ? storeIds : undefined,
    }),
    enabled: !!brandId,
  })

  if (isLoading) {
    return (
      <div className="bg-card rounded-lg shadow-sm border border-border p-6">
        <p className="text-muted-foreground text-center">Carregando comparação de lojas...</p>
      </div>
    )
  }

  if (!data || !data.stores || data.stores.length === 0) {
    return (
      <div className="bg-card rounded-lg shadow-sm border border-border p-6">
        <div className="flex items-center gap-2 mb-4">
          <Store className="w-5 h-5 text-primary" />
          <h3 className="text-lg font-semibold text-card-foreground">
            Comparação de Performance das Lojas
          </h3>
        </div>
        <div className="text-center py-8">
          <p className="text-muted-foreground">
            Nenhuma loja encontrada com os filtros selecionados
          </p>
        </div>
      </div>
    )
  }

  const stores: StoreMetrics[] = data.stores

  // Build filter labels
  const weekdayNames = ['Domingo', 'Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado']
  const channelNames: Record<number, string> = {
    1: 'Presencial',
    2: 'iFood',
    3: 'Rappi',
    4: 'Uber Eats',
    5: 'WhatsApp',
    6: 'App Próprio',
  }

  const contextLabel = []
  if (contextFilters?.weekday !== undefined) {
    contextLabel.push(weekdayNames[contextFilters.weekday])
  }
  if (contextFilters?.hourStart !== undefined && contextFilters?.hourEnd !== undefined) {
    contextLabel.push(`${contextFilters.hourStart}h-${contextFilters.hourEnd}h`)
  }
  if (contextFilters?.channelId !== undefined) {
    contextLabel.push(channelNames[contextFilters.channelId])
  }

  const storeFilterLabel = storeIds && storeIds.length > 0 
    ? `${storeIds.length} loja${storeIds.length > 1 ? 's' : ''}`
    : null

  // Prepare chart data - ordenado por faturamento (do maior para o menor)
  const chartData = stores.map((store, index) => ({
    name: store.store_name.length > 25 
      ? `${store.store_name.substring(0, 22)}...` 
      : store.store_name,
    fullName: store.store_name,
    revenue: store.total_revenue,
    sales: store.total_sales,
    ticket: store.average_ticket,
    share: store.revenue_share,
    color: COLORS[index % COLORS.length],
    city: store.city || '-',
    state: store.state || '-',
  }))

  const maxRevenue = Math.max(...chartData.map(d => d.revenue))

  return (
    <div className="bg-card rounded-lg shadow-sm border border-border p-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-2">
          <Store className="w-5 h-5 text-primary" />
          <h3 className="text-lg font-semibold text-card-foreground">
            Comparação de Performance das Lojas
            {contextLabel.length > 0 && (
              <span className="text-muted-foreground font-normal"> - {contextLabel.join(' • ')}</span>
            )}
          </h3>
        </div>
        {storeFilterLabel && (
          <span className="text-xs bg-primary/10 text-primary px-2 py-1 rounded-md font-medium">
            {storeFilterLabel}
          </span>
        )}
      </div>

      {/* Gráfico de Barras Horizontais - apenas se houver mais de uma loja */}
      {stores.length > 1 && (
        <div className="mb-6">
          <div className="mb-2 flex items-center justify-between">
            <p className="text-sm text-muted-foreground">Faturamento Total</p>
            <p className="text-xs text-muted-foreground">
              {stores.length} loja{stores.length > 1 ? 's' : ''}
            </p>
          </div>
          <div style={{ height: Math.max(200, stores.length * 30) }} className="w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={chartData}
                layout="vertical"
                margin={{ top: 5, right: 20, left: 10, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis 
                  type="number" 
                  tickFormatter={(value) => formatCurrency(value, 0)}
                  stroke="#6b7280"
                  fontSize={12}
                />
                <YAxis 
                  type="category" 
                  dataKey="name" 
                  hide={true}
                />
                <Tooltip
                  content={({ active, payload }) => {
                    if (active && payload && payload.length) {
                      const data = payload[0].payload
                      return (
                        <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-3 shadow-lg">
                          <p className="font-semibold text-sm mb-2">{data.fullName}</p>
                          <div className="space-y-1 text-xs">
                            <div className="flex justify-between gap-4">
                              <span className="text-muted-foreground">Faturamento:</span>
                              <span className="font-semibold">{formatCurrency(data.revenue)}</span>
                            </div>
                            <div className="flex justify-between gap-4">
                              <span className="text-muted-foreground">Participação:</span>
                              <span className="font-semibold">{formatPercent(data.share)}</span>
                            </div>
                            <div className="flex justify-between gap-4">
                              <span className="text-muted-foreground">Vendas:</span>
                              <span>{formatNumber(data.sales)}</span>
                            </div>
                            <div className="flex justify-between gap-4">
                              <span className="text-muted-foreground">Ticket Médio:</span>
                              <span>{formatCurrency(data.ticket)}</span>
                            </div>
                            {data.city && (
                              <div className="flex justify-between gap-4">
                                <span className="text-muted-foreground">Local:</span>
                                <span>{data.city}, {data.state}</span>
                              </div>
                            )}
                          </div>
                        </div>
                      )
                    }
                    return null
                  }}
                />
                <Bar dataKey="revenue" radius={[0, 8, 8, 0]}>
                  {chartData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {/* Tabela Detalhada */}
      <div className={stores.length > 1 ? "mt-6 pt-6 border-t border-border" : ""}>
        <h4 className="text-sm font-semibold text-card-foreground mb-4 flex items-center gap-2">
          <TrendingUp className="w-4 h-4 text-primary" />
          Detalhamento Completo
        </h4>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-border">
                <th className="text-left py-3 px-4 text-sm font-semibold text-muted-foreground">
                  Loja
                </th>
                <th className="text-left py-3 px-4 text-sm font-semibold text-muted-foreground">
                  Local
                </th>
                <th className="text-right py-3 px-4 text-sm font-semibold text-muted-foreground">
                  Faturamento
                </th>
                <th className="text-right py-3 px-4 text-sm font-semibold text-muted-foreground">
                  Participação
                </th>
                <th className="text-right py-3 px-4 text-sm font-semibold text-muted-foreground">
                  Vendas
                </th>
                <th className="text-right py-3 px-4 text-sm font-semibold text-muted-foreground">
                  Ticket Médio
                </th>
              </tr>
            </thead>
            <tbody>
              {stores.map((store, index) => (
                <tr
                  key={store.store_id}
                  className="border-b border-border last:border-0 hover:bg-primary/5 transition-colors"
                >
                  <td className="py-3 px-4">
                    <div className="flex items-center gap-2">
                      <div
                        className="w-3 h-3 rounded-full"
                        style={{ backgroundColor: COLORS[index % COLORS.length] }}
                      />
                      <p className="text-sm font-medium text-card-foreground">
                        {store.store_name}
                      </p>
                    </div>
                  </td>
                  <td className="py-3 px-4 text-sm text-muted-foreground">
                    {store.city && store.state ? (
                      <span className="flex items-center gap-1">
                        <MapPin className="w-3 h-3" />
                        {store.city}, {store.state}
                      </span>
                    ) : (
                      '-'
                    )}
                  </td>
                  <td className="py-3 px-4 text-sm text-right font-semibold text-primary">
                    {formatCurrency(store.total_revenue)}
                  </td>
                  <td className="py-3 px-4 text-sm text-right text-muted-foreground">
                    {formatPercent(store.revenue_share)}
                  </td>
                  <td className="py-3 px-4 text-sm text-right text-card-foreground">
                    {formatNumber(store.total_sales)}
                  </td>
                  <td className="py-3 px-4 text-sm text-right text-muted-foreground">
                    {formatCurrency(store.average_ticket)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

